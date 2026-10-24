// SPDX-License-Identifier: GPL-2.0-or-later
// Read a single compositor eye through Valve's public diagnostic API.
// Supply openvr_capi.h on the include path; use a private VR_PATHREG_OVERRIDE for simulation.
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <string>
#include <windows.h>
#include <d3d11.h>
#include <wrl/client.h>
#include "openvr_capi.h"

using Microsoft::WRL::ComPtr;

int main(int argc, char** argv) {
    if (argc != 3) {
        std::fprintf(stderr, "Usage: openvr_mirror_probe openvr_api.dll output-prefix\n");
        return 2;
    }
    const auto dll = LoadLibraryA(argv[1]);
    if (!dll) return 3;
    const auto init = reinterpret_cast<intptr_t (*)(EVRInitError*, EVRApplicationType)>(
        GetProcAddress(dll, "VR_InitInternal"));
    const auto shutdown = reinterpret_cast<void (*)()>(GetProcAddress(dll, "VR_ShutdownInternal"));
    const auto get = reinterpret_cast<void* (*)(const char*, EVRInitError*)>(
        GetProcAddress(dll, "VR_GetGenericInterface"));
    if (!init || !shutdown || !get) return 4;
    EVRInitError error{};
    init(&error, EVRApplicationType_VRApplication_Background);
    if (error) { std::fprintf(stderr, "OpenVR init: %d\n", error); return 5; }
    const auto table = static_cast<VR_IVRCompositor_FnTable*>(
        get("FnTable:IVRCompositor_027", &error));
    if (!table) { shutdown(); return 6; }
    ComPtr<ID3D11Device> device;
    ComPtr<ID3D11DeviceContext> context;
    if (FAILED(D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, 0, nullptr, 0,
                                 D3D11_SDK_VERSION, &device, nullptr, &context))) {
        shutdown(); return 7;
    }
    int result = 0;
    // Keep both requests alive while the compositor starts updating its shared mirrors.
    // An immediate first read can return an old/blank right-eye image.
    void* live_views[2]{};
    for (int eye = 0; eye < 2; ++eye) {
        table->GetMirrorTextureD3D11(static_cast<EVREye>(eye), device.Get(), &live_views[eye]);
    }
    Sleep(500);
    for (int eye = 0; eye < 2; ++eye) {
        void* view{};
        const auto status = table->GetMirrorTextureD3D11(static_cast<EVREye>(eye), device.Get(), &view);
        if (status || !view) {
            std::fprintf(stderr, "Mirror eye %d: %d\n", eye, status); result = 8; continue;
        }
        ComPtr<ID3D11Resource> resource;
        static_cast<ID3D11ShaderResourceView*>(view)->GetResource(&resource);
        ComPtr<ID3D11Texture2D> texture;
        if (FAILED(resource.As(&texture))) {
            table->ReleaseMirrorTextureD3D11(view); result = 9; continue;
        }
        D3D11_TEXTURE2D_DESC desc{};
        texture->GetDesc(&desc);
        D3D11_SHADER_RESOURCE_VIEW_DESC view_desc{};
        static_cast<ID3D11ShaderResourceView*>(view)->GetDesc(&view_desc);
        unsigned mip = 0, slice = 0;
        if (view_desc.ViewDimension == D3D11_SRV_DIMENSION_TEXTURE2D) {
            mip = view_desc.Texture2D.MostDetailedMip;
        } else if (view_desc.ViewDimension == D3D11_SRV_DIMENSION_TEXTURE2DARRAY) {
            mip = view_desc.Texture2DArray.MostDetailedMip;
            slice = view_desc.Texture2DArray.FirstArraySlice;
        } else {
            table->ReleaseMirrorTextureD3D11(view); result = 9; continue;
        }
        const auto subresource = D3D11CalcSubresource(mip, slice, desc.MipLevels);
        desc.Width = (desc.Width >> mip) ? (desc.Width >> mip) : 1;
        desc.Height = (desc.Height >> mip) ? (desc.Height >> mip) : 1;
        desc.Format = view_desc.Format;
        std::printf("Eye %d: %ux%u format %u samples %u\n", eye, desc.Width, desc.Height,
                    desc.Format, desc.SampleDesc.Count);
        const bool rgba = desc.Format == DXGI_FORMAT_R8G8B8A8_UNORM ||
                          desc.Format == DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
        const bool bgra = desc.Format == DXGI_FORMAT_B8G8R8A8_UNORM ||
                          desc.Format == DXGI_FORMAT_B8G8R8A8_UNORM_SRGB;
        if ((!rgba && !bgra) || desc.SampleDesc.Count != 1) {
            table->ReleaseMirrorTextureD3D11(view); result = 9; continue;
        }
        desc.Usage = D3D11_USAGE_STAGING;
        desc.BindFlags = 0; desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
        desc.MiscFlags = 0; desc.ArraySize = 1; desc.MipLevels = 1;
        ComPtr<ID3D11Texture2D> staging;
        if (FAILED(device->CreateTexture2D(&desc, nullptr, &staging))) {
            table->ReleaseMirrorTextureD3D11(view); result = 10; continue;
        }
        context->CopySubresourceRegion(staging.Get(), 0, 0, 0, 0, texture.Get(), subresource, nullptr);
        D3D11_MAPPED_SUBRESOURCE mapped{};
        if (SUCCEEDED(context->Map(staging.Get(), 0, D3D11_MAP_READ, 0, &mapped))) {
            std::ofstream out(std::string(argv[2]) + (eye ? "-right.ppm" : "-left.ppm"),
                              std::ios::binary);
            out << "P6\n" << desc.Width << " " << desc.Height << "\n255\n";
            for (unsigned y = 0; y < desc.Height; ++y) {
                const auto row = static_cast<const unsigned char*>(mapped.pData) + y * mapped.RowPitch;
                for (unsigned x = 0; x < desc.Width; ++x) {
                    const unsigned char rgb[]{row[x*4+(bgra ? 2 : 0)], row[x*4+1],
                                              row[x*4+(bgra ? 0 : 2)]};
                    out.write(reinterpret_cast<const char*>(rgb), 3);
                }
            }
            context->Unmap(staging.Get(), 0);
            if (!out) result = 11;
        } else result = 12;
        table->ReleaseMirrorTextureD3D11(view);
    }
    for (void* view : live_views) {
        if (view) table->ReleaseMirrorTextureD3D11(view);
    }
    shutdown();
    FreeLibrary(dll);
    return result;
}

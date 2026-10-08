/* Documented NMOS 6502 opcode layout: mnemonic, mode, cycles, page/branch penalty. */
(function (root) {
  "use strict";
  const OPCODES = "BRK imp 7 0|ORA inx 6 0||||ORA zpg 3 0|ASL zpg 5 0||PHP imp 3 0|ORA imm 2 0|ASL acc 2 0|||ORA abs 4 0|ASL abs 6 0||BPL rel 2 2|ORA iny 5 1||||ORA zpx 4 0|ASL zpx 6 0||CLC imp 2 0|ORA aby 4 1||||ORA abx 4 1|ASL abx 7 0||JSR abs 6 0|AND inx 6 0|||BIT zpg 3 0|AND zpg 3 0|ROL zpg 5 0||PLP imp 4 0|AND imm 2 0|ROL acc 2 0||BIT abs 4 0|AND abs 4 0|ROL abs 6 0||BMI rel 2 2|AND iny 5 1||||AND zpx 4 0|ROL zpx 6 0||SEC imp 2 0|AND aby 4 1||||AND abx 4 1|ROL abx 7 0||RTI imp 6 0|EOR inx 6 0||||EOR zpg 3 0|LSR zpg 5 0||PHA imp 3 0|EOR imm 2 0|LSR acc 2 0||JMP abs 3 0|EOR abs 4 0|LSR abs 6 0||BVC rel 2 2|EOR iny 5 1||||EOR zpx 4 0|LSR zpx 6 0||CLI imp 2 0|EOR aby 4 1||||EOR abx 4 1|LSR abx 7 0||RTS imp 6 0|ADC inx 6 0||||ADC zpg 3 0|ROR zpg 5 0||PLA imp 4 0|ADC imm 2 0|ROR acc 2 0||JMP ind 5 0|ADC abs 4 0|ROR abs 6 0||BVS rel 2 2|ADC iny 5 1||||ADC zpx 4 0|ROR zpx 6 0||SEI imp 2 0|ADC aby 4 1||||ADC abx 4 1|ROR abx 7 0|||STA inx 6 0|||STY zpg 3 0|STA zpg 3 0|STX zpg 3 0||DEY imp 2 0||TXA imp 2 0||STY abs 4 0|STA abs 4 0|STX abs 4 0||BCC rel 2 2|STA iny 6 0|||STY zpx 4 0|STA zpx 4 0|STX zpy 4 0||TYA imp 2 0|STA aby 5 0|TXS imp 2 0|||STA abx 5 0|||LDY imm 2 0|LDA inx 6 0|LDX imm 2 0||LDY zpg 3 0|LDA zpg 3 0|LDX zpg 3 0||TAY imp 2 0|LDA imm 2 0|TAX imp 2 0||LDY abs 4 0|LDA abs 4 0|LDX abs 4 0||BCS rel 2 2|LDA iny 5 1|||LDY zpx 4 0|LDA zpx 4 0|LDX zpy 4 0||CLV imp 2 0|LDA aby 4 1|TSX imp 2 0||LDY abx 4 1|LDA abx 4 1|LDX aby 4 1||CPY imm 2 0|CMP inx 6 0|||CPY zpg 3 0|CMP zpg 3 0|DEC zpg 5 0||INY imp 2 0|CMP imm 2 0|DEX imp 2 0||CPY abs 4 0|CMP abs 4 0|DEC abs 3 0||BNE rel 2 2|CMP iny 5 1||||CMP zpx 4 0|DEC zpx 6 0||CLD imp 2 0|CMP aby 4 1||||CMP abx 4 1|DEC abx 7 0||CPX imm 2 0|SBC inx 6 0|||CPX zpg 3 0|SBC zpg 3 0|INC zpg 5 0||INX imp 2 0|SBC imm 2 0|NOP imp 2 0||CPX abs 4 0|SBC abs 4 0|INC abs 6 0||BEQ rel 2 2|SBC iny 5 1||||SBC zpx 4 0|INC zpx 6 0||SED imp 2 0|SBC aby 4 1||||SBC abx 4 1|INC abx 7 0|".split("|").map(entry => {
    if (!entry) return null;
    const [op, mode, cycles, extra] = entry.split(" ");
    return { op, mode, cycles: Number(cycles), extra: Number(extra) };
  });
  class Cpu6502 {
    constructor(memory = new Uint8Array(65536)) {
      this.memory = memory;
      this.a = 0; this.x = 0; this.y = 0; this.sp = 255;
      this.p = 0x30; this.pc = 0; this.cycles = 0;
    }
    read(address) { return this.memory[address & 65535]; }
    write(address, value) { this.memory[address & 65535] = value & 255; }
    word(address) { return this.read(address) | (this.read(address + 1) << 8); }
    wrappedWord(address) {
      return this.read(address) | (this.read((address & 0xff00) | ((address + 1) & 255)) << 8);
    }
    fetch() { const value = this.read(this.pc); this.pc = (this.pc + 1) & 65535; return value; }
    push(value) { this.write(0x100 + this.sp, value); this.sp = (this.sp - 1) & 255; }
    pop() { this.sp = (this.sp + 1) & 255; return this.read(0x100 + this.sp); }
    pushWord(value) { this.push(value >> 8); this.push(value); }
    popWord() { const low = this.pop(); return low | (this.pop() << 8); }
    nz(value) {
      value &= 255;
      this.p = (this.p & ~0x82) | (value ? value & 128 : 2);
      return value;
    }
    flag(mask, enabled) { this.p = (this.p & ~mask) | (enabled ? mask : 0); }
    irq() {
      if (this.p & 4) return false;
      this.pushWord(this.pc);
      this.p &= ~16;
      this.push(this.p | 32);
      this.p |= 4;
      this.pc = this.word(0xfffe);
      this.cycles += 7;
      return true;
    }
    arithmetic(value, subtract) {
      const a = this.a, carry = this.p & 1;
      if (!(this.p & 8)) {
        const operand = subtract ? value ^ 255 : value;
        const sum = a + operand + carry;
        this.flag(64, (~(a ^ operand) & (a ^ sum) & 128) !== 0);
        this.flag(1, sum > 255);
        this.a = this.nz(sum);
        return;
      }
      // NMOS decimal correction; N/Z/V come from the pre-correction ALU result.
      if (subtract) {
        const sum = a + (value ^ 255) + carry;
        let lo = (a & 15) - (value & 15) - (1 - carry);
        let hi = (a >> 4) - (value >> 4);
        if (lo < 0) { lo -= 6; hi--; }
        if (hi < 0) hi -= 6;
        this.nz(sum);
        this.flag(64, ((a ^ value) & (a ^ sum) & 128) !== 0);
        this.flag(1, sum > 255);
        this.a = ((hi << 4) | (lo & 15)) & 255;
      } else {
        const low = (a & 15) + (value & 15) + carry;
        const high = (a >> 4) + (value >> 4) + (low > 9 ? 1 : 0);
        const alu = ((high & 15) << 4) | (low & 15);
        this.nz(alu);
        this.flag(64, (~(a ^ value) & (a ^ alu) & 128) !== 0);
        this.flag(1, high > 9);
        this.a = ((((high + (high > 9 ? 6 : 0)) & 15) << 4) |
          ((low + (low > 9 ? 6 : 0)) & 15));
      }
    }
    step() {
      const start = this.pc, code = this.fetch(), instruction = OPCODES[code];
      if (!instruction) throw new Error(`Unsupported 6502 opcode $${code.toString(16)} at $${start.toString(16)}`);
      const { op, mode, extra } = instruction;
      let address = 0, base = 0, penalty = 0;
      switch (mode) {
        case "imm": address = this.pc; this.fetch(); break;
        case "zpg": address = this.fetch(); break;
        case "zpx": address = (this.fetch() + this.x) & 255; break;
        case "zpy": address = (this.fetch() + this.y) & 255; break;
        case "abs": address = this.fetch(); address |= this.fetch() << 8; break;
        case "abx": case "aby":
          base = this.fetch(); base |= this.fetch() << 8;
          address = (base + (mode === "abx" ? this.x : this.y)) & 65535;
          if (extra && (address & 0xff00) !== (base & 0xff00)) penalty++;
          break;
        case "inx": address = this.wrappedWord((this.fetch() + this.x) & 255); break;
        case "iny":
          base = this.wrappedWord(this.fetch()); address = (base + this.y) & 65535;
          if (extra && (address & 0xff00) !== (base & 0xff00)) penalty++;
          break;
        case "ind": base = this.fetch(); base |= this.fetch() << 8; address = this.wrappedWord(base); break;
        case "rel":
          base = this.fetch(); address = (this.pc + (base < 128 ? base : base - 256)) & 65535;
          break;
      }
      const value = mode === "acc" ? this.a : this.read(address);
      const store = result => { if (mode === "acc") this.a = result & 255; else this.write(address, result); };
      const compare = register => {
        this.flag(1, register >= value); this.nz(register - value);
      };
      const branch = condition => {
        if (!condition) return;
        penalty = 1 + ((this.pc & 0xff00) !== (address & 0xff00) ? 1 : 0); this.pc = address;
      };
      switch (op) {
        case "LDA": this.a = this.nz(value); break;
        case "LDX": this.x = this.nz(value); break;
        case "LDY": this.y = this.nz(value); break;
        case "STA": this.write(address, this.a); break;
        case "STX": this.write(address, this.x); break;
        case "STY": this.write(address, this.y); break;
        case "TAX": this.x = this.nz(this.a); break;
        case "TAY": this.y = this.nz(this.a); break;
        case "TXA": this.a = this.nz(this.x); break;
        case "TYA": this.a = this.nz(this.y); break;
        case "TSX": this.x = this.nz(this.sp); break;
        case "TXS": this.sp = this.x; break;
        case "PHA": this.push(this.a); break;
        case "PHP": this.push(this.p | 48); break;
        case "PLA": this.a = this.nz(this.pop()); break;
        case "PLP": this.p = this.pop() | 48; break;
        case "AND": this.a = this.nz(this.a & value); break;
        case "ORA": this.a = this.nz(this.a | value); break;
        case "EOR": this.a = this.nz(this.a ^ value); break;
        case "ADC": this.arithmetic(value, false); break;
        case "SBC": this.arithmetic(value, true); break;
        case "CMP": compare(this.a); break;
        case "CPX": compare(this.x); break;
        case "CPY": compare(this.y); break;
        case "BIT": this.p = (this.p & ~0xc2) | (value & 0xc0) | ((this.a & value) ? 0 : 2); break;
        case "ASL": this.flag(1, value & 128); store(this.nz(value << 1)); break;
        case "LSR": this.flag(1, value & 1); store(this.nz(value >> 1)); break;
        case "ROL": {
          const carry = this.p & 1; this.flag(1, value & 128); store(this.nz((value << 1) | carry)); break;
        }
        case "ROR": {
          const carry = this.p & 1; this.flag(1, value & 1); store(this.nz((value >> 1) | (carry << 7))); break;
        }
        case "INC": this.write(address, this.nz(value + 1)); break;
        case "DEC": this.write(address, this.nz(value - 1)); break;
        case "INX": this.x = this.nz(this.x + 1); break;
        case "INY": this.y = this.nz(this.y + 1); break;
        case "DEX": this.x = this.nz(this.x - 1); break;
        case "DEY": this.y = this.nz(this.y - 1); break;
        case "CLC": this.p &= ~1; break;
        case "SEC": this.p |= 1; break;
        case "CLD": this.p &= ~8; break;
        case "SED": this.p |= 8; break;
        case "CLI": this.p &= ~4; break;
        case "SEI": this.p |= 4; break;
        case "CLV": this.p &= ~64; break;
        case "BPL": branch(!(this.p & 128)); break;
        case "BMI": branch(this.p & 128); break;
        case "BVC": branch(!(this.p & 64)); break;
        case "BVS": branch(this.p & 64); break;
        case "BCC": branch(!(this.p & 1)); break;
        case "BCS": branch(this.p & 1); break;
        case "BNE": branch(!(this.p & 2)); break;
        case "BEQ": branch(this.p & 2); break;
        case "JMP": this.pc = address; break;
        case "JSR": this.pushWord((this.pc - 1) & 65535); this.pc = address; break;
        case "RTS": this.pc = (this.popWord() + 1) & 65535; break;
        case "RTI": this.p = this.pop() | 48; this.pc = this.popWord(); break;
        case "BRK":
          this.pushWord((this.pc + 1) & 65535); this.p |= 16; this.push(this.p | 48);
          this.p |= 4; this.pc = this.word(0xfffe); break;
        case "NOP": break;
        default: throw new Error(`Unimplemented instruction ${op}`);
      }
      this.cycles += instruction.cycles + penalty;
      return this;
    }
  }
  if (typeof module !== "undefined" && module.exports) module.exports = { Cpu6502 };
  else root.PetCpu = { Cpu6502 };
})(typeof globalThis !== "undefined" ? globalThis : this);

"""Optional browser integration check: requires Python playwright and Chromium.
Start the project server separately, then run this script.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import argparse
import shutil

parser = argparse.ArgumentParser(description="Check the PET character edition in Chromium")
parser.add_argument("--url", default="http://127.0.0.1:8080/")
parser.add_argument("--chromium", default=shutil.which("chromium"))
parser.add_argument("--screenshots", default="/tmp/pet-browser-qa")
args = parser.parse_args()
output = Path(args.screenshots)
output.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1280,'height':1000})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 capture_game = '''Object.defineProperty(window,"PetInvaders",{configurable:true,set(api){const Base=api.Game;api.Game=class extends Base{constructor(...args){super(...args);window.__testGame=this;}};Object.defineProperty(window,"PetInvaders",{value:api,writable:true,configurable:true});}});'''
 page.add_init_script(capture_game)
 page.goto(args.url)
 assert page.locator('#game').get_attribute('width')=='320'
 assert page.locator('#game').get_attribute('height')=='200'
 assert page.evaluate('__testGame.screen.length')==1000
 page.screenshot(path=str(output / "menu.png"),full_page=True)
 page.keyboard.press('b');page.wait_for_timeout(150)
 assert page.evaluate('__testGame.state')=='playing'
 x=page.evaluate('__testGame.player.x')
 page.keyboard.down('=');page.wait_for_timeout(400);page.keyboard.up('=')
 assert page.evaluate('__testGame.player.x')>x
 page.keyboard.down('Space');page.wait_for_timeout(70)
 assert page.evaluate('__testGame.memory[0x35]')==0
 page.keyboard.up('Space')
 page.keyboard.press('p');page.wait_for_timeout(50)
 cycles=page.evaluate('__testGame.cpu.cycles');page.wait_for_timeout(150)
 assert page.evaluate('__testGame.cpu.cycles')==cycles
 page.locator('#start').click();assert page.evaluate('__testGame.state')=='playing'
 page.locator('#settings').click();assert page.evaluate('__testGame.state')=='paused'
 page.locator('#starting-lives').select_option('3');page.locator('#delay').select_option('20')
 page.locator('button[type=submit]').click();page.wait_for_timeout(100)
 assert page.evaluate('__testGame.state')=='playing'
 page.keyboard.press('[');assert page.evaluate('__testGame.state')=='over'
 page.locator('#start').click();page.wait_for_function('__testGame.lives === 3')
 assert page.evaluate('__testGame.memory[0x12e8]')==20
 page.wait_for_timeout(500)
 # Freeze simulation through the test harness; the delivered game has no debug globals.
 page.evaluate('__testGame.update = () => {}')
 page.wait_for_timeout(50)
 # Canvas contains exactly the character RAM raster (not overlay sprites or browser text).
 assert page.evaluate('''() => {
  const actual=document.getElementById("game").getContext("2d").getImageData(0,0,320,200).data;
  const expected=PetInvaders.rasterize(__testGame.screen);
  return actual.every((byte,i)=>byte===expected[i]);
 }''')
 page.screenshot(path=str(output / "game.png"),full_page=True)
 assert not errors,errors
 mobile=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 mobile.add_init_script(capture_game)
 mobile.on('pageerror',lambda e:errors.append(str(e)))
 mobile.goto(args.url)
 assert mobile.evaluate('document.documentElement.scrollWidth')<=390
 mobile.locator('#start').click();assert mobile.locator('#fire').is_visible()
 # Real touch input through Chromium's device protocol, including press/release.
 mobile.wait_for_timeout(200)
 before=mobile.evaluate('__testGame.player.x')
 button=mobile.locator('#right').bounding_box()
 touch=mobile.context.new_cdp_session(mobile)
 touch.send('Input.dispatchTouchEvent', {'type':'touchStart','touchPoints':[{'x':button['x']+button['width']/2,'y':button['y']+button['height']/2}]})
 mobile.wait_for_timeout(200)
 touch.send('Input.dispatchTouchEvent', {'type':'touchEnd','touchPoints':[]})
 assert mobile.evaluate('__testGame.player.x')>before
 assert not mobile.locator('#right').evaluate('element=>element.classList.contains("held")')
 mobile.locator('#settings').click();assert mobile.locator('#setup-dialog').is_visible()
 assert mobile.evaluate('document.documentElement.scrollWidth')<=390
 mobile.locator('#cancel-setup').click();mobile.wait_for_timeout(100)
 mobile.screenshot(path=str(output / "mobile.png"),full_page=True)
 assert not errors,errors
 b.close()
 print('PASS: original character screen raster, B/= /Space/[ controls, pause/resume, real PET parameters, mobile touch movement/layout; no JS errors')

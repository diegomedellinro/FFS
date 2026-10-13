// Identidad DigitalDreams: logo, tipografía con serifa y ajustes de color
// compartidos por render.js (carruseles) y motion.js (videos).
const fs = require('fs');
const path = require('path');

const b64 = (f) => fs.readFileSync(path.join(__dirname, f)).toString('base64');
const LOGO = `data:image/svg+xml;base64,${b64('logo-icono.svg')}`;

module.exports = `
@font-face { font-family: 'Crimson Pro'; font-weight: 200 900; src: url(data:font/ttf;base64,${b64('fonts/CrimsonPro[wght].ttf')}); }
.dot { width: 44px !important; height: 44px !important; border-radius: 4px !important; background: url(${LOGO}) center/cover !important; }
.wm { font-family: 'Crimson Pro', serif; font-size: 40px; font-weight: 400; letter-spacing: 0; color: #fff; }
.top { align-items: center; color: #A3D98A; }
h1, h2, .quote { font-family: 'Crimson Pro', serif; letter-spacing: -.015em !important; }
h1 { font-weight: 700 !important; } h2, .quote { font-weight: 650 !important; }
.btn, .action, .right .bubble, .tick { color: #031203 !important; }
.good .label { color: #8FF20E !important; } .good { border-color: rgba(143,242,14,.55) !important; background: rgba(143,242,14,.07) !important; }
.r0 .pill { background: #4DBA12 !important; color: #031203; }
.blob { opacity: .5; } .b1, .b2 { opacity: .5; } .b3 { opacity: .14; }
`;

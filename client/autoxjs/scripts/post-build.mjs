import fs from 'node:fs'

const content = fs.readFileSync('dist/index.js', 'utf-8')
fs.writeFileSync('dist/index.js', '"ui";\n' + content, 'utf-8')

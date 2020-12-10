const fs   = require('fs');
const path = require("path");
const loader = require('speccy/lib/loader');

const outputDir = './dist';
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, 0744);
}

loader
    .loadSpec('./key-locator-api.yaml', {resolve: true})
    .then(spec => JSON.stringify(spec, null, 2))
    .then(specStr => fs.writeFile(path.join(outputDir, 'key-locator-api.json'), specStr, (err) => {if (err) throw err}))
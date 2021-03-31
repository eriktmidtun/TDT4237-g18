// Prerequiquisites:
// `npm install --save qrcode` while in same folder as package.json
// `npm install -g browserify` to use commands in terminal

// This function uses node and is translated using browserify

// First, cd to Scripts-folder
// ... then run `browserify displayQR_orig.js -o displayQR.js`
//                         (file translates to desired file)

const QRCode = require('qrcode')

window.addEventListener("DOMContentLoaded", async () => {

    const canvas = document.getElementById('displayqr')
    let response = await sendRequest("GET", `${HOST}/api/users/two_factor/totp_uri/`);

    if (response.ok) {
        let data = await response.json();

        QRCode.toCanvas(canvas, data, (error) => {
        if (error) console.error(error)
        })
    }
})

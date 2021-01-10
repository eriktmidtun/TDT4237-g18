function replace_default_setting(fs, filename, settings) {
    console.log(`Replacing settings for file ${filename}`)
    var data = fs.readFileSync(filename, 'utf8');
    var result = data;

    for (var setting in settings) {
        var re = new RegExp(`(\\s*const\\s+${setting}\\s*=\\s*")(.*)("\\s*;)`);
        result = result.replace(re, `$1${settings[setting]}$3`) + '\n';
        console.log(`New host: ${result}`);
    }

    fs.writeFileSync(filename, result, 'utf8');
}

module.exports = function(context) {
    // adapted from https://medium.com/@farazpatankar/hooking-up-with-cordova-d16bc4f4b755
    console.log('Running hook...');

    var fs = require('fs');
    var path = require('path');

    if (process.env.BACKEND_HOST) {
        console.log("BACKEND_HOST is " + process.env.BACKEND_HOST);
        // Specify the files you would like to replace.
        // NOTE: The android path is for Cordova 7.
        // If you're running an older version, the path is:
        // "platforms/android/assets/www/index.html"
        var configFilesToReplace = {
            browser: 'platforms/browser/www/scripts/defaults.js',
            android: 'platforms/android/app/src/main/assets/www/scripts/defaults.js'
        };

        for (var platform of context.opts.cordova.platforms) {
            var destFile = path.join(configFilesToReplace[platform]);
            console.log(
            'Modifying config for platform ' +
                platform
            );

            replace_default_setting(fs, destFile, {'HOST': process.env.BACKEND_HOST});
            
        }
    } else {
        console.log('HOST variable not set.  Using default value.');
    }
}


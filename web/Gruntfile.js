module.exports = function(grunt) {

    grunt.initConfig({

        pkg: grunt.file.readJSON('package.json'),

        dest: {
            js: {
                main: '<%= pkg.dest.js %>main.bundle.js',
            },
        },

        browserify: {
  
            dist: {
                options: {
                    transform: [['babelify', {
                        'presets': ['es2015', 'react'],
                        'plugins': ['transform-react-jsx'],
                    }]]
                },
                files: {
                    '<%= dest.js.main %>': [
                        'scripts/components/*.jsx',
                    ],
                }
            }
        },

        uglify: {
            options: {
                compress: {
                    //drop_console: true // removing console.log() statements
                }
            },
            my_target: {
                files: {
                   '<%= dest.js.main %>': ['<%= dest.js.main %>']
                }
            }
        },
    });


    grunt.loadNpmTasks('grunt-browserify');
    grunt.loadNpmTasks('grunt-contrib-uglify');

    grunt.registerTask('default', [
        'browserify',
        //'uglify',
    ]);
};

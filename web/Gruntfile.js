
// grunt entry point
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

        concat: {
            options: {
                separator: '\r\n',
            },


            /*
             * CSS
             */
/*
            

            main_css: {
                src: [
                    'css/fonts.css',
                    'css/lib/bootstrap/3.3.5/bootstrap.min.css',
                    'css/lib/dropzone.css',
                    'css/lib/filepicker.css',
                    'css/lib/spinner.css',
                    'css/main.style.css'
                ],
                dest: '<%= pkg.dest.css %>main.style.css'
            },

            download_css: {
                src: [
                    'css/lib/bootstrap/3.3.5/bootstrap.min.css',
                    'css/intro.style.css',
                    'css/download.style.css'
                ],
                dest: '<%= pkg.dest.css %>download.style.css'
            },
*/



            /*
             * Javascript
             */

            main_js: {
                src: [
                    'scripts/lib/jquery.min.js',

                    '<%= dest.js.main %>'
                ],
                dest: '<%= dest.js.main %>'
            },

        },


        cssmin: {
            styles: {
                options: {
                    banner: '/*! <%= grunt.template.today("mm-dd-yyyy") %> */\n'
                },                
                files: {
                    //'<%= concat.intro_css.dest %>': ['<%= concat.intro_css.dest %>'],
                    //'<%= concat.main_css.dest %>': ['<%= concat.main_css.dest %>'],
                    //'<%= concat.download_css.dest %>': ['<%= concat.download_css.dest %>']
                },
            },
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


        cacheBust: {
            taskName: {
                options: {
                    separator: '-',
                    deleteOriginals: true,
                    assets: ['scripts/dist/*', 'css/dist/*'],
                },
                src: ['<%= pkg.dest.module %>Assets.php']
            }
        },


    });



    grunt.loadNpmTasks('grunt-browserify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-cssmin');

    grunt.loadNpmTasks('grunt-contrib-uglify');


    grunt.loadNpmTasks('grunt-cache-bust');
    //grunt.loadNpmTasks('grunt-contrib-watch');
    


    grunt.registerTask('default', [
        'browserify',
        //'concat',
        //'cssmin',
        //'uglify',
        //'cacheBust'
        //'watch'
    ]);
};

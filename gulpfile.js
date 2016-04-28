// process.chdir('djangocms_comments/static/djangocms_comments');
var gulp = require('gulp'),
    compass = require('gulp-compass');
    cleanCSS = require('gulp-clean-css');
    uglify = require('gulp-uglify');
    concat = require('gulp-concat');


var SRCS = {
    boostrap3: 'djangocms_comments/boilerplates/bootstrap3/static/djangocms_comments',
    main: 'djangocms_comments/static/djangocms_comments'
};

JS_FILES = ['src/js/comments.js', 'src/libs/autosize/dist/autosize.js', 'src/libs/blueimp-md5/dist/md5.js'];

var defaultTasks = ['minify-js'];

// CSS

function staticCSS(src){
    var cwd = SRCS[src];
    gulp.task(src + '-sass', function () {

        return gulp.src('src/scss/*.scss', {cwd: cwd})
            .pipe(compass({
                // project_path: cwd,
                css: cwd + '/dist/css',
                sass: cwd + '/src/scss',
                environment: 'production'
            }))
    });

    gulp.task(src + '-minify-css', [src + '-sass'], function () {
        return gulp.src('dist/css/*.css', {cwd: cwd})
            .pipe(cleanCSS())
            .pipe(gulp.dest('dist/css/'));
    });
}

for (var key in SRCS) {
    staticCSS(key);
    defaultTasks.push(key + '-minify-css');
}

gulp.task('minify-js', function () {
    return gulp.src(JS_FILES, {cwd: SRCS['main']})
        .pipe(concat('comments.min.js'))
        .pipe(uglify({
            // project_path: cwd,
        }))
        .pipe(gulp.dest(SRCS['main'] + '/dist/js/'));
});


gulp.task('default', defaultTasks);

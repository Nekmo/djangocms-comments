// process.chdir('djangocms_comments/static/djangocms_comments');
var gulp = require('gulp'),
    compass = require('gulp-compass');
    cleanCSS = require('gulp-clean-css');
    var gutil = require('gulp-util');

var defaultTasks = [];

// CSS
var srcs = {
    boostrap3: 'djangocms_comments/boilerplates/bootstrap3/static/djangocms_comments',
    main: 'djangocms_comments/static/djangocms_comments'
};

function staticCSS(src){
    var cwd = srcs[src];
    gulp.task(src + '-sass', function () {
        gutil.log(cwd);
        return gulp.src('src/scss/*.scss', {cwd: cwd})
            .pipe(compass({
                // project_path: cwd,
                css: cwd + '/dist/css',
                sass: cwd + '/src/scss',
                debug: true,
                environment: 'production'
            }))
    });

    gulp.task(src + '-minify-css', [src + '-sass'], function () {
        return gulp.src('dist/css/*.css', {cwd: cwd})
            .pipe(cleanCSS())
            .pipe(gulp.dest('dist/css/'));
    });
}

for (var key in srcs) {
    staticCSS(key);
    defaultTasks.push(key + '-minify-css');
}

gulp.task('default', defaultTasks);

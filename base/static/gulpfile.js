var gulp = require('gulp'),
   less = require('gulp-less'),
   autoprefix = require('gulp-autoprefixer');

gulp.task('less', function () {
   gulp.src('less/main.less')
      .pipe(less())
      .pipe(autoprefix('last 2 version', 'ie 8', 'ie 9'))
      .pipe(gulp.dest('css'));
});

var watchPaths = {
    less: [
        './less/**/*'
    ]
};

gulp.task('default', ['less'], function() {
    gulp.watch(watchPaths.less, ['less']);
});
var gulp       = require('gulp');
var clean      = require('gulp-clean');
var concat     = require('gulp-concat');
var less       = require('gulp-less');
var cleanCSS   = require('gulp-clean-css');
var autoprefixer = require('gulp-autoprefixer');

// AUTOPREFIX SETTINGS
var browsers = ["firefox > 3.6","ie >= 9","chrome >= 32","ios_saf >= 5","safari >= 5","opera > 0"];

var LessPluginAutoPrefix = require('less-plugin-autoprefix');
var lessAutoprefixPlugin = new LessPluginAutoPrefix({
    browsers: browsers
});

var CSS_BUNDLE_NAME = 'main.min.css';

var ICEDITOR_PUBLIC_FOLDER = 'src/main/java/com/lorepo/iceditor/public';
var DIST_CSS_FOLDER = ICEDITOR_PUBLIC_FOLDER + '/dist';
var SRC_LESS_FILES = ICEDITOR_PUBLIC_FOLDER + '/**/*.less';


gulp.task('default', ['dist-css'] );
gulp.task('clean', ['clean']);


/* CSS DISTRIBUTION */
gulp.task('dist-css', ['concat-css']);

gulp.task('concat-css', ['less'], function() {
    return gulp
        .src(DIST_CSS_FOLDER + '/**/*.css')
        .pipe(cleanCSS({
            rebase: false
        }))
        .pipe(concat(CSS_BUNDLE_NAME))
        .pipe(gulp.dest(DIST_CSS_FOLDER));
});

gulp.task('less', function() {
    return gulp
        .src(SRC_LESS_FILES)
        .pipe(less({
            plugins: [lessAutoprefixPlugin]
        }))
        .pipe(gulp.dest(DIST_CSS_FOLDER));
});

gulp.task('clean', function () {
    return gulp
        .src(DIST_CSS_FOLDER, {
            read: false
        })
        .pipe(clean());
});
/* --- END CSS DISTRIBUTION --- */
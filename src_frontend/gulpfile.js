var gulp         = require('gulp');
var clean        = require('gulp-clean');
var concat       = require('gulp-concat');
var sass         = require('gulp-sass');
var cleanCSS     = require('gulp-clean-css');
var autoprefixer = require('gulp-autoprefixer');
var shell        = require('gulp-shell');


var DIST_CSS_FOLDER =  'css';
var BUILD_FOLDER = '../src/mauthor/templates/static_files/frontend';
var BUILD_SRC = [
    'dist/**',
    'libs/**',
    'assets/**',
    'css/main.min.css'
];

gulp.task('default', ['compile-and-copy']);

gulp.task('dev', ['compile-and-copy-dev']);

function copyBuild () {
    return gulp
        .src(BUILD_SRC, { base: '.' })
        .pipe(gulp.dest(BUILD_FOLDER));
}

gulp.task('compile-and-copy', ['compile-ts', 'compile-scss', 'clear-compilation'], copyBuild);

gulp.task('compile-and-copy-dev', ['compile-ts-dev', 'compile-scss', 'clear-compilation'], copyBuild);

gulp.task('compile-ts', shell.task(['ng build --prod --aot']));

gulp.task('hot', shell.task(['ng serve --proxy-config proxy.config.json']));

gulp.task('compile-ts-dev', shell.task(['ng build']));

/* COMPILE SCSS */
var autoprefixerBrowsers = [
    "firefox > 3.6","ie >= 9","chrome >= 32","safari >= 5","opera > 0",
    "ios_saf >= 5",
    "android >= 2.2","and_chr > 0","and_ff > 0","and_uc > 0",
    "ie_mob > 0",
    "operamobile > 0"
];

gulp.task('compile-scss', ['concat-css']);

gulp.task('concat-css', ['autoprefixer'], function() {
    return gulp
        .src(DIST_CSS_FOLDER + '/**/*.css')
        .pipe(cleanCSS())
        .pipe(concat('main.min.css'))
        .pipe(gulp.dest(DIST_CSS_FOLDER));
});

gulp.task('autoprefixer', ['sass'], function() {
    return gulp.src([
        DIST_CSS_FOLDER + '/**/*.css',
        '!' + DIST_CSS_FOLDER + '/**/material-blue-pink.css'  // excludes Angular Material 2 library styles
    ])
    .pipe(autoprefixer({
        browsers: autoprefixerBrowsers,
        cascade: false
    }))
    .pipe(gulp.dest(DIST_CSS_FOLDER));
});

gulp.task('sass', ['clean-css'], function() {
    return gulp
        .src(['src/app/*/templates/**/*.scss', 'src/app/*/component/**/*.scss'])
        .pipe(sass.sync().on('error', sass.logError))
        .pipe(gulp.dest(DIST_CSS_FOLDER));
});

gulp.task('clean-css', function () {
    return gulp
        .src(DIST_CSS_FOLDER, {
            read: false
        })
        .pipe(clean());
});
/* --- END COMPILE SCSS --- */

gulp.task('clear-compilation', function () {
    return gulp
        .src(BUILD_FOLDER, {
          read: false
        })
        .pipe(clean({ force: true }));
});

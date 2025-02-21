var gulp         = require('gulp');
var clean        = require('gulp-clean');
var concat       = require('gulp-concat');
var sass         = require('gulp-sass');
var cleanCSS     = require('gulp-clean-css');
var autoprefixer = require('gulp-autoprefixer');
var typescript   = require('gulp-tsc');
var shell        = require('gulp-shell');
var tsConfig     = require('./tsconfig.json');

// AUTOPREFIXER SETTINGS
var autoprefixerBrowsers = [
    "firefox > 3.6","ie >= 9","chrome >= 32","safari >= 5","opera > 0",
    "ios_saf >= 5",
    "android >= 2.2","and_chr > 0","and_ff > 0","and_uc > 0",
    "ie_mob > 0",
    "operamobile > 0"
];

var DIST_FOLDER = 'dist';
var DIST_CSS_FOLDER =  'css';
var DIST_LIBS_FOLDER = DIST_FOLDER + '/libraries';
var WEBPACK_FOLDER = 'bundle';
var BUILD_FOLDER = '../src/mauthor/templates/static_files/frontend';

var LIB_FILES = [
    'node_modules/core-js/client/shim.min.js',
    'node_modules/core-js/client/shim.map',
    'node_modules/reflect-metadata/Reflect.js',
    'node_modules/reflect-metadata/Reflect.js.map',
    'node_modules/zone.js/dist/zone.min.js',
    'node_modules/hammerjs/hammer.min.js'
];

var BUILD_SRC = [
    'dist/**'
];

gulp.task('default', ['copy-build']);

gulp.task('dev', ['copy-build-dev']);

gulp.task('build', ['dist-css', 'dist-js']);

gulp.task('build-dev', ['dist-css', 'dev-js']);

gulp.task('clean', ['clean-css', 'clean-libs', 'clean-tsc', 'clean-ngc', 'clean-webpack']);

/* --- COPY BUILD --- */
gulp.task('copy-build', ['clean-build', 'build', 'copy-libs', 'copy-assets'], function() {
    return gulp
        .src(BUILD_SRC, {base: '.'})
        .pipe(gulp.dest(BUILD_FOLDER));
});

gulp.task('copy-build-dev', ['clean-build', 'build-dev', 'copy-libs', 'copy-assets'], function() {
    return gulp
        .src(BUILD_SRC, {base: '.'})
        .pipe(gulp.dest(BUILD_FOLDER));
});

gulp.task('clean-build', function() {
    return gulp
        .src([BUILD_FOLDER], {
            read: false
        })
        .pipe(clean({force: true}));
});

gulp.task('copy-assets', function () {
  return gulp
        .src('assets/**/*', {base: '.'})
        .pipe(gulp.dest(BUILD_FOLDER));
});
/* --- END COPY BUILD --- */


/* CSS DISTRIBUTION */
gulp.task('dist-css', ['concat-css']);

gulp.task('concat-css', ['autoprefixer'], function() {
    return gulp
        .src(DIST_CSS_FOLDER + '/**/*.css')
        .pipe(cleanCSS())
        .pipe(concat('main.min.css'))
        .pipe(gulp.dest(BUILD_FOLDER + '/css'));
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
        .src('src/app/*/templates/**/*.scss')
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
/* --- END CSS DISTRIBUTION --- */


/* JAVASCRIPT DEVELOPMENT MODE */
gulp.task('dev-js', ['webpack-dev']);

    // JAVASCRIPT DISTRIBUTION :: RUN WEBPACK BUNDLER IN DEVELOPMENT MODE
gulp.task('webpack-dev', ['clean-webpack', 'clean-tsc', 'clean-ngc'],
    shell.task(['ng build'])
);
/* --- END JAVASCRIPT DEVELOPMENT MODE --- */


/* JAVASCRIPT DISTRIBUTION */
gulp.task('dist-js', ['webpack']);

    // JAVASCRIPT DISTRIBUTION :: RUN WEBPACK BUNDLER
gulp.task('webpack', ['clean-webpack'],
    shell.task(['ng build --aot'])
);

gulp.task('clean-webpack', function () {
    return gulp
        .src(WEBPACK_FOLDER, {
            read: false
        })
        .pipe(clean());
});

    // JAVASCRIPT DISTRIBUTION :: COPY LIBRARIES
gulp.task('copy-libs', ['clean-libs'], function() {
    return gulp
        .src('libs/**/*')
        .pipe(gulp.dest(BUILD_FOLDER + '/libs'));
});

gulp.task('clean-libs', function () {
    return gulp
        .src('dist/libs', {
            read: false
        })
        .pipe(clean());
});

    // JAVASCRIPT DISTRIBUTION :: RUN TYPESCRIPT COMPILATION
gulp.task('tsc', ['clean-tsc', 'clean-ngc'], function() {
    return gulp
        .src([
            'typings/browser.d.ts',
            'app/**/*.ts',
            '!app/**/*.aot.ts',
            '!app/**/*.ngfactory.ts'
        ])
        .pipe(typescript(tsConfig.compilerOptions))
        .pipe(gulp.dest('.'));
});

gulp.task('clean-tsc', function() {
    return gulp
        .src([
            'app/**/*.js',
            'app/**/*.js.map'
        ], {
            read: false
        })
        .pipe(clean());
});

    // JAVASCRIPT DISTRIBUTION :: RUN ANGULAR 2 AHEAD-OF-TIME COMPILATION
gulp.task('ngc', ['clean-ngc', 'clean-tsc'], shell.task(['npm run ngc']));

gulp.task('clean-ngc', function () {
    return gulp
        .src([
            'app/**/*.ngfactory.ts',
            'app/**/*.metadata.json'
        ], {
            read: false
        })
        .pipe(clean());
});
/* --- END JAVASCRIPT DISTRIBUTION --- */

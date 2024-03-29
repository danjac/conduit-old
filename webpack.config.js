const path = require('path');
const isProduction = process.env.NODE_ENV === 'production';

module.exports = {
  mode: process.env.NODE_ENV,
  entry: path.resolve(__dirname, 'static', 'js', 'app.js'),
  output: {
    path: path.resolve(__dirname, 'static', isProduction ? 'dist' : 'dev'),
    filename: 'app.js',
  },
  resolve: {
    alias: {
      '~': path.resolve(__dirname, 'static', 'js'),
    },
  },
  watch: !isProduction,
  watchOptions: {
    ignored: ['node_modules/**'],
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
            plugins: [
              '@babel/plugin-proposal-class-properties',
              '@babel/transform-runtime',
            ],
          },
        },
      },
    ],
  },
};

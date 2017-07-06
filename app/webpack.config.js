var webpack = require('webpack');

module.exports = {  
  entry: {
    app: ["./static/components/app.js"],
    monitor: ["./static/components/monitor.js"]
  },
  output: {
    path: __dirname + '/static',
    filename: "[name].bundle.js"
  },
  module: {
    loaders: [
      {
        test: /\.js?$/,
        loader: 'babel-loader',
        query: {
          presets: ['es2015', 'react', 'stage-2']
        },
        exclude: /node_modules/
      }
    ]
  },
  plugins: [ ]
};

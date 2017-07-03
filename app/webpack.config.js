var webpack = require('webpack');

module.exports = {  
  entry: [
    "./static/components/app.js"
  ],
  output: {
    path: __dirname + '/static',
    filename: "bundle.js"
  },
  module: {
    loaders: [
      {
        test: /\.js?$/,
        loader: 'babel-loader',
        query: {
          presets: ['es2015', 'react']
        },
        exclude: /node_modules/
      }
    ]
  },
    plugins: [
	// new webpack.DefinePlugin({
	//     'process.env':{
	// 	'NODE_ENV': JSON.stringify('production')
	//     }
	// }),
	// new webpack.optimize.UglifyJsPlugin({
	//     compress:{
	// 	warnings: true
	//     }
	// })
    ]
};

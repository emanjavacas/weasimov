
# WeAsimov app

## Prerequisites

You'll need some package managers.

- `npm`
- `pip`

`npm` typically bundles with `node` itself. To get `node` you would probably like some kind of node version manager like `n` (the only one I've ever used).

## Setup

For the frontend:

If you don't have webpack, install it:

```
npm install -g webpack
```

Then, use `npm` to install the remaining JavaScript dependencies.

```
npm install
```

## Development

The entry point for the app is in `static/components/app.js`.

While developing on the frontend, run `webpack --watch` to keep re-compiling your JavaScript code.

Running `webpack` creates a file in `static/bundle.js`, which is the bundled version of your frontend code.

## Running the app

Run the Flask app

```
python run.py
```


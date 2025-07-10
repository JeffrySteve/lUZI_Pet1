# Virtual Cat Application

This project is a virtual cat application that provides an interactive experience with a virtual cat. The cat can perform various animations and respond to user interactions.

## Project Structure

```
pet-app
├── src
│   ├── assets
│   │   ├── cat_idle.gif
│   │   ├── cat.gif
│   │   ├── loading_cat.gif
│   │   └── sleepy_cat.gif
│   └── pet.py
├── requirements.txt
├── setup.py
└── README.md
```

## Installation

To run this application, you need to install the required dependencies. You can do this by running:

```
pip install -r requirements.txt
```

## Running the Application

To start the virtual cat application, execute the following command:

```
python src/pet.py
```

## Creating an Executable

To package the application into an executable, you can use the `setup.py` file. Run the following command:

```
python setup.py build
```

This will create an executable version of the application that you can run without needing to have Python installed.

## Animations

The application includes the following animations for the virtual cat:

- `cat_idle.gif`: Animation for the idle state.
- `cat.gif`: Animation for the talking state.
- `loading_cat.gif`: Animation for the loading state.
- `sleepy_cat.gif`: Animation for the sleeping state.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests. Your feedback and contributions are welcome!
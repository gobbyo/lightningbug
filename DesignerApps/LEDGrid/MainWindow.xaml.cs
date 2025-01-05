using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Shapes;
using System.Windows.Controls;

namespace LEDGrid
{
    public partial class MainWindow : Window
    {
        private const int DefaultLEDWidth = 30;
        private const int DefaultLEDHeight = 50;
        private LEDLayoutManager LEDLayoutManager;
        private GridDisplay gridDisplay;

        public MainWindow()
        {
            InitializeComponent();
            this.Width = 800;
            this.Height = 600;

            this.MouseDown += Window_MouseDown;
            this.KeyDown += Window_KeyDown;
            this.Closing += MainWindow_Closing;
            this.Loaded += MainWindow_Loaded;

            int rectangleWidth = DefaultLEDWidth;
            int rectangleHeight = DefaultLEDHeight;

            // Load grid size from JSON file if available
            if (File.Exists("rectangle_positions.json"))
            {
                var json = File.ReadAllText("rectangle_positions.json");
                var saveData = JsonSerializer.Deserialize<SaveData>(json);
                if (saveData != null)
                {
                    rectangleWidth = saveData.Width;
                    rectangleHeight = saveData.Height;
                }
            }

            gridDisplay = new GridDisplay(MainCanvas, rectangleWidth, rectangleHeight);
            LEDLayoutManager = new LEDLayoutManager(MainCanvas, rectangleWidth, rectangleHeight, gridDisplay);
            LEDLayoutManager.LoadLEDPositions();
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            gridDisplay.PaintGrid();
        }

        private void Window_MouseDown(object sender, MouseButtonEventArgs e)
        {
            var position = e.GetPosition(MainCanvas); // Get the position relative to MainCanvas

            // Snap the position to the nearest grid cell
            int cellX = (int)(position.X / LEDLayoutManager.Width);
            int cellY = (int)(position.Y / LEDLayoutManager.Height);
            int posX = cellX * LEDLayoutManager.Width;
            int posY = cellY * LEDLayoutManager.Height;

            // Check if the click is within any existing rectangle
            var rectangleToRemove = MainCanvas.Children.OfType<Grid>()
                .FirstOrDefault(container =>
                {
                    var left = Canvas.GetLeft(container);
                    var top = Canvas.GetTop(container);
                    return posX == left && posY == top;
                });

            if (rectangleToRemove != null)
            {
                MainCanvas.Children.Remove(rectangleToRemove);
                var rectPosToRemove = LEDLayoutManager.LEDPositions.FirstOrDefault(rp =>
                    rp.CellX == cellX && rp.CellY == cellY);
                if (rectPosToRemove != null)
                {
                    LEDLayoutManager.LEDPositions.Remove(rectPosToRemove);
                    LEDLayoutManager.RenumberLEDs();
                }
            }
            else
            {
                // Check if the cell is already occupied
                bool isCellOccupied = LEDLayoutManager.LEDPositions.Any(rp => rp.CellX == cellX && rp.CellY == cellY);

                if (!isCellOccupied)
                {
                    LEDLayoutManager.AddLabeledLED(cellX, cellY, posX, posY);
                }
            }

            // Ensure the grid is repainted with numbers
            gridDisplay.PaintGrid();
        }

        private void Window_KeyDown(object sender, KeyEventArgs e)
        {
            if (Keyboard.IsKeyDown(Key.LeftShift) || Keyboard.IsKeyDown(Key.RightShift))
            {
                if (e.Key == Key.Up)
                {
                    LEDLayoutManager.ResizeLEDs(0, 1);
                }
                else if (e.Key == Key.Down)
                {
                    LEDLayoutManager.ResizeLEDs(0, -1);
                }
                else if (e.Key == Key.Left)
                {
                    LEDLayoutManager.ResizeLEDs(-1, 0);
                }
                else if (e.Key == Key.Right)
                {
                    LEDLayoutManager.ResizeLEDs(1, 0);
                }
            }
            else
            {
                if (e.Key == Key.Left)
                {
                    LEDLayoutManager.MoveLEDs(-1, 0);
                }
                else if (e.Key == Key.Right)
                {
                    LEDLayoutManager.MoveLEDs(1, 0);
                }
                else if (e.Key == Key.Up)
                {
                    LEDLayoutManager.MoveLEDs(0, -1);
                }
                else if (e.Key == Key.Down)
                {
                    LEDLayoutManager.MoveLEDs(0, 1);
                }
            }

            // Ensure the grid is repainted with numbers
            gridDisplay.PaintGrid();
        }

        private void MainWindow_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            LEDLayoutManager.SaveLEDPositions();
        }
    }
}
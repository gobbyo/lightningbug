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
        private List<LED> newSequenceLEDs = new List<LED>();

        public MainWindow()
        {
            InitializeComponent();
            this.Width = SystemParameters.PrimaryScreenWidth;
            this.Height = SystemParameters.PrimaryScreenHeight;

            this.MouseDown += Window_MouseDown;
            this.KeyDown += Window_KeyDown;
            this.KeyUp += Window_KeyUp;
            this.Closing += MainWindow_Closing;
            this.Loaded += MainWindow_Loaded;
            this.MouseWheel += Window_MouseWheel; // Add MouseWheel event handler

            int rectangleWidth = DefaultLEDWidth;
            int rectangleHeight = DefaultLEDHeight;

            // Load grid size from JSON file if available
            if (File.Exists("led_positions.json"))
            {
                var json = File.ReadAllText("led_positions.json");
                var saveData = JsonSerializer.Deserialize<SaveData>(json);
                if (saveData != null)
                {
                    rectangleWidth = saveData.Width;
                    rectangleHeight = saveData.Height;
                }
            }

            if (MainCanvas != null)
            {
                gridDisplay = new GridDisplay(MainCanvas, rectangleWidth, rectangleHeight);
                LEDLayoutManager = new LEDLayoutManager(MainCanvas, 24, 24, gridDisplay); // Initialize with 12 by 12 cells
                LEDLayoutManager.LoadLEDPositions();
            }
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            gridDisplay.PaintGrid();
        }

        private void MainWindow_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            gridDisplay.PaintGrid(); // Repaint the grid when the window size changes
        }

        private void Window_MouseDown(object sender, MouseButtonEventArgs e)
        {
            if (MainCanvas == null) return;

            var position = e.GetPosition(MainCanvas); // Get the position relative to MainCanvas

            // Snap the position to the nearest grid cell
            int cellX = (int)(position.X / LEDLayoutManager.Width);
            int cellY = (int)(position.Y / LEDLayoutManager.Height);
            int posX = cellX * LEDLayoutManager.Width;
            int posY = cellY * LEDLayoutManager.Height;

            if (Keyboard.IsKeyDown(Key.LeftCtrl) || Keyboard.IsKeyDown(Key.RightCtrl))
            {
                // Handle Ctrl + Left Mouse Click to add LEDs to the new sequence
                var led = LEDLayoutManager.LEDPositions.FirstOrDefault(rp => rp.CellX == cellX && rp.CellY == cellY);
                if (led != null)
                {
                    var newLed = new LED
                    {
                        Ref = led.Ref,
                        CellX = led.CellX,
                        CellY = led.CellY,
                        Lumin = led.Lumin,
                        SleepSec = led.SleepSec,
                        WaitSec = led.WaitSec
                    };

                    newSequenceLEDs.Add(newLed);
                    HighlightLED(posX, posY);
                    UpdateNewJsonTextBox();
                }
            }
            else
            {
                // Handle normal left mouse click
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
                    bool isCellOccupied = LEDLayoutManager.LEDPositions.Any(rp => rp.CellX == cellX && rp.CellY == cellY);

                    if (!isCellOccupied)
                    {
                        LEDLayoutManager.AddLabeledLED(cellX, cellY, posX, posY);
                    }
                }

                gridDisplay.PaintGrid();
            }
        }

        private void HighlightLED(int posX, int posY)
        {
            if (MainCanvas == null) return;

            var highlightRectangle = new Rectangle
            {
                Width = LEDLayoutManager.Width,
                Height = LEDLayoutManager.Height,
                Fill = Brushes.Yellow,
                Opacity = 0.5
            };

            Canvas.SetLeft(highlightRectangle, posX);
            Canvas.SetTop(highlightRectangle, posY);

            MainCanvas.Children.Add(highlightRectangle);
        }

        private void UpdateNewJsonTextBox()
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = true
            };
            var json = JsonSerializer.Serialize(newSequenceLEDs, options);
            NewJsonTextBox.Text = json;
        }

        private void Window_KeyUp(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.LeftCtrl || e.Key == Key.RightCtrl)
            {
                SaveNewSequence();
            }
        }

        private void SaveNewSequence()
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = true
            };
            var json = JsonSerializer.Serialize(newSequenceLEDs, options);
            File.WriteAllText("led_sequence.json", json);
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

            gridDisplay.PaintGrid();
        }

        private void Window_MouseWheel(object sender, MouseWheelEventArgs e)
        {
            if (MainCanvas == null) return;

            double offsetX = 0;
            double offsetY = 0;

            if (Keyboard.IsKeyDown(Key.LeftShift) || Keyboard.IsKeyDown(Key.RightShift))
            {
                // Scroll horizontally when Shift key is pressed
                offsetX = e.Delta > 0 ? -10 : 10;
            }
            else
            {
                // Scroll vertically by default
                offsetY = e.Delta > 0 ? -10 : 10;
            }

            double newOffsetX = MainCanvas.RenderTransform.Value.OffsetX + offsetX;
            double newOffsetY = MainCanvas.RenderTransform.Value.OffsetY + offsetY;

            var transform = new TranslateTransform(newOffsetX, newOffsetY);
            MainCanvas.RenderTransform = transform;

            gridDisplay.PaintGrid(newOffsetX, newOffsetY); // Pass the new offsets to PaintGrid
        }

        private void MainWindow_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            LEDLayoutManager.SaveLEDPositions();
        }
    }
}
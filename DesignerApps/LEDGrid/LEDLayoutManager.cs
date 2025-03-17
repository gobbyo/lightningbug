using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Shapes;

namespace LEDGrid
{
    public class LEDLayoutManager
    {
        private readonly Canvas mainCanvas;
        private readonly GridDisplay gridDisplay;
        private int rectangleWidth;
        private int rectangleHeight;
        private List<LED> layout = new List<LED>();
        public List<LED> LEDPositions { get; private set; } = new List<LED>();

        public int Width => rectangleWidth;
        public int Height => rectangleHeight;

        public LEDLayoutManager(Canvas canvas, int rectWidth, int rectHeight, GridDisplay display)
        {
            mainCanvas = canvas;
            rectangleWidth = rectWidth;
            rectangleHeight = rectHeight;
            gridDisplay = display;
            //UpdateGridSize(64, 64); // Set grid to 64 by 64 cells
        }

        public void UpdateGridSize(int width, int height)
        {
            rectangleWidth = width;
            rectangleHeight = height;

            // Clear and repaint all rectangles with updated sizes
            var gridLines = mainCanvas.Children.OfType<Line>().Where(line => line.Stroke == Brushes.DarkGray).ToList();
            mainCanvas.Children.Clear();
            foreach (var line in gridLines)
            {
                mainCanvas.Children.Add(line);
            }
            foreach (var pos in LEDPositions)
            {
                PaintLED(pos.CellX * rectangleWidth, pos.CellY * rectangleHeight, pos.CellX, pos.CellY, pos.Ref);
            }

            // Update the grid size
            gridDisplay.UpdateGridSize(rectangleWidth, rectangleHeight);
        }

        public void AddLabeledLED(int cellX, int cellY, int posX, int posY)
        {
            AddLEDToList(cellX, cellY);
            RenumberLEDs();
        }

        public void PaintLED(int posX, int posY, int cellX, int cellY, int seq)
        {
            var newRectangle = new Rectangle
            {
                Width = rectangleWidth,
                Height = rectangleHeight,
                Fill = Brushes.Black
            };

            var label = new TextBlock
            {
                Text = $"{seq}\nX: {cellX}\nY: {cellY}",
                Foreground = Brushes.White,
                FontSize = 12,
                Width = rectangleWidth,
                Height = rectangleHeight,
                TextAlignment = System.Windows.TextAlignment.Center,
                VerticalAlignment = System.Windows.VerticalAlignment.Center
            };

            var container = new Grid
            {
                Width = rectangleWidth,
                Height = rectangleHeight
            };

            container.Children.Add(newRectangle);
            container.Children.Add(label);

            Canvas.SetLeft(container, posX);
            Canvas.SetTop(container, posY);

            mainCanvas.Children.Add(container);
        }

        public void AddLEDToList(int cellX, int cellY)
        {
            LEDPositions.Add(new LED { CellX = cellX, CellY = cellY });
        }

        public void RenumberLEDs()
        {
            int newSeq = 0;
            foreach (var rectPos in LEDPositions)
            {
                rectPos.Ref = newSeq++;
            }

            // Clear and repaint all rectangles with updated sequence numbers
            var gridLines = mainCanvas.Children.OfType<Line>().Where(line => line.Stroke == Brushes.DarkGray).ToList();
            mainCanvas.Children.Clear();
            foreach (var line in gridLines)
            {
                mainCanvas.Children.Add(line);
            }
            foreach (var pos in LEDPositions)
            {
                PaintLED(pos.CellX * rectangleWidth, pos.CellY * rectangleHeight, pos.CellX, pos.CellY, pos.Ref);
            }
        }

        public void MoveLEDs(int deltaX, int deltaY)
        {
            foreach (var rectPos in LEDPositions)
            {
                rectPos.CellX += deltaX;
                rectPos.CellY += deltaY;
            }

            // Clear and repaint all rectangles with updated positions
            var gridLines = mainCanvas.Children.OfType<Line>().Where(line => line.Stroke == Brushes.DarkGray).ToList();
            mainCanvas.Children.Clear();
            foreach (var line in gridLines)
            {
                mainCanvas.Children.Add(line);
            }
            foreach (var pos in LEDPositions)
            {
                PaintLED(pos.CellX * rectangleWidth, pos.CellY * rectangleHeight, pos.CellX, pos.CellY, pos.Ref);
            }
        }

        public void ResizeLEDs(int deltaX, int deltaY)
        {
            rectangleWidth = Math.Max(1, rectangleWidth + deltaX);
            rectangleHeight = Math.Max(1, rectangleHeight + deltaY);

            // Clear and repaint all rectangles with updated sizes
            var gridLines = mainCanvas.Children.OfType<Line>().Where(line => line.Stroke == Brushes.DarkGray).ToList();
            mainCanvas.Children.Clear();
            foreach (var line in gridLines)
            {
                mainCanvas.Children.Add(line);
            }
            foreach (var pos in LEDPositions)
            {
                PaintLED(pos.CellX * rectangleWidth, pos.CellY * rectangleHeight, pos.CellX, pos.CellY, pos.Ref);
            }

            // Update the grid size
            gridDisplay.UpdateGridSize(rectangleWidth, rectangleHeight);
        }

        public void SaveLEDPositions()
        {
            var saveData = new SaveData
            {
                LEDPositions = LEDPositions,
                Width = rectangleWidth,
                Height = rectangleHeight
            };

            var options = new JsonSerializerOptions
            {
                WriteIndented = true
            };
            var json = JsonSerializer.Serialize(saveData, options);
            File.WriteAllText("led_positions.json", json);
        }

        public void LoadLEDPositions()
        {
            if (File.Exists("led_positions.json"))
            {
                var json = File.ReadAllText("led_positions.json");
                var saveData = JsonSerializer.Deserialize<SaveData>(json);

                LEDPositions = saveData.LEDPositions;
                rectangleWidth = saveData.Width;
                rectangleHeight = saveData.Height;

                RenumberLEDs();
            }
        }
    }
}
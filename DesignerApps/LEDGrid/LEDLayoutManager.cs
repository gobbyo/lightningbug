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
        private List<LEDPosition> layout = new List<LEDPosition>();
        public List<LEDPosition> LEDPositions { get; private set; } = new List<LEDPosition>();

        public int RectangleWidth => rectangleWidth;
        public int RectangleHeight => rectangleHeight;

        public LEDLayoutManager(Canvas canvas, int rectWidth, int rectHeight, GridDisplay display)
        {
            mainCanvas = canvas;
            rectangleWidth = rectWidth;
            rectangleHeight = rectHeight;
            gridDisplay = display;
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
            LEDPositions.Add(new LEDPosition { CellX = cellX, CellY = cellY });
        }

        public void RenumberLEDs()
        {
            int newSeq = 1;
            foreach (var rectPos in LEDPositions)
            {
                rectPos.Seq = newSeq++;
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
                PaintLED(pos.CellX * rectangleWidth, pos.CellY * rectangleHeight, pos.CellX, pos.CellY, pos.Seq);
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
                PaintLED(pos.CellX * rectangleWidth, pos.CellY * rectangleHeight, pos.CellX, pos.CellY, pos.Seq);
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
                PaintLED(pos.CellX * rectangleWidth, pos.CellY * rectangleHeight, pos.CellX, pos.CellY, pos.Seq);
            }

            // Update the grid size
            gridDisplay.UpdateGridSize(rectangleWidth, rectangleHeight);
        }

        public void SaveLEDPositions()
        {
            var saveData = new SaveData
            {
                LEDPositions = LEDPositions,
                RectangleWidth = rectangleWidth,
                RectangleHeight = rectangleHeight
            };

            var options = new JsonSerializerOptions
            {
                WriteIndented = true
            };
            var json = JsonSerializer.Serialize(saveData, options);
            File.WriteAllText("rectangle_positions.json", json);
        }

        public void LoadLEDPositions()
        {
            if (File.Exists("rectangle_positions.json"))
            {
                var json = File.ReadAllText("rectangle_positions.json");
                var saveData = JsonSerializer.Deserialize<SaveData>(json);

                LEDPositions = saveData.LEDPositions;
                rectangleWidth = saveData.RectangleWidth;
                rectangleHeight = saveData.RectangleHeight;

                RenumberLEDs();
            }
        }
    }
}
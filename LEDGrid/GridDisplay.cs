using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Shapes;
using System.Linq;

namespace LEDGrid
{
    public class GridDisplay
    {
        private readonly Canvas mainCanvas;
        private int rectangleWidth;
        private int rectangleHeight;

        public GridDisplay(Canvas canvas, int rectWidth, int rectHeight)
        {
            mainCanvas = canvas;
            rectangleWidth = rectWidth;
            rectangleHeight = rectHeight;
            PaintGrid();
        }

        public void UpdateGridSize(int newRectWidth, int newRectHeight)
        {
            rectangleWidth = newRectWidth;
            rectangleHeight = newRectHeight;
            PaintGrid();
        }

        public void PaintGrid()
        {
            mainCanvas.Children.OfType<Line>()
                .Where(line => line.Stroke == Brushes.DarkGray)
                .ToList()
                .ForEach(line => mainCanvas.Children.Remove(line));

            mainCanvas.Children.OfType<TextBlock>()
                .Where(textBlock => textBlock.Foreground == Brushes.Black)
                .ToList()
                .ForEach(textBlock => mainCanvas.Children.Remove(textBlock));

            for (int x = 0; x < mainCanvas.ActualWidth; x += rectangleWidth)
            {
                var verticalLine = new Line
                {
                    X1 = x,
                    Y1 = 0,
                    X2 = x,
                    Y2 = mainCanvas.ActualHeight,
                    Stroke = Brushes.DarkGray,
                    StrokeThickness = 1
                };
                mainCanvas.Children.Add(verticalLine);

                // Add cell number across the first row
                var cellNumber = new TextBlock
                {
                    Text = (x / rectangleWidth).ToString(),
                    Foreground = Brushes.Black,
                    FontSize = 12,
                    Width = rectangleWidth,
                    Height = rectangleHeight,
                    TextAlignment = System.Windows.TextAlignment.Center,
                    VerticalAlignment = System.Windows.VerticalAlignment.Center
                };
                Canvas.SetLeft(cellNumber, x);
                Canvas.SetTop(cellNumber, 0);
                mainCanvas.Children.Add(cellNumber);
            }

            for (int y = 0; y < mainCanvas.ActualHeight; y += rectangleHeight)
            {
                var horizontalLine = new Line
                {
                    X1 = 0,
                    Y1 = y,
                    X2 = mainCanvas.ActualWidth,
                    Y2 = y,
                    Stroke = Brushes.DarkGray,
                    StrokeThickness = 1
                };
                mainCanvas.Children.Add(horizontalLine);

                // Add cell number down the first column
                var cellNumber = new TextBlock
                {
                    Text = (y / rectangleHeight).ToString(),
                    Foreground = Brushes.Black,
                    FontSize = 12,
                    Width = rectangleWidth,
                    Height = rectangleHeight,
                    TextAlignment = System.Windows.TextAlignment.Center,
                    VerticalAlignment = System.Windows.VerticalAlignment.Center
                };
                Canvas.SetLeft(cellNumber, 0);
                Canvas.SetTop(cellNumber, y);
                mainCanvas.Children.Add(cellNumber);
            }
        }
    }
}
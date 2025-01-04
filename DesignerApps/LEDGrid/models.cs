using System.Collections.Generic;

namespace LEDGrid
{
    public class SaveData
    {
        public int RectangleWidth { get; set; }
        public int RectangleHeight { get; set; }
        public List<RectanglePosition> RectanglePositions { get; set; }
    }

    public class RectanglePosition
    {
        public int Seq { get; set; }
        public int CellX { get; set; }
        public int CellY { get; set; }
    }
}
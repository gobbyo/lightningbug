using System.Collections.Generic;

namespace LEDGrid
{
    public class SaveData
    {
        public int RectangleWidth { get; set; }
        public int RectangleHeight { get; set; }
        public List<LEDPosition> LEDPositions { get; set; }
    }

    public class LEDPosition
    {
        public int Seq { get; set; }
        public int CellX { get; set; }
        public int CellY { get; set; }
    }
}
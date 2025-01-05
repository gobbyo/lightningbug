using System.Collections.Generic;

namespace LEDGrid
{
    public class SaveData
    {
        public int RectangleWidth { get; set; }
        public int RectangleHeight { get; set; }
        public List<LED> LEDPositions { get; set; }
    }

    public class LED
    {
        public int Seq { get; set; }
        public int CellX { get; set; }
        public int CellY { get; set; }
        public int Lumin { get; set; } = 4096;
        public double SleepSec { get; set; } = 0.25;
        public double WaitSec { get; set; } = 0.125;
    }
}
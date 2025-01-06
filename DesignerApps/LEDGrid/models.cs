using System.Collections.Generic;

namespace LEDGrid
{
    public class SaveData
    {
        public int Width { get; set; }
        public int Height { get; set; }
        public List<LED> LEDPositions { get; set; }
    }

    public class LED
    {
        public int Ref { get; set; }
        public int CellX { get; set; }
        public int CellY { get; set; }
        public int Lumin { get; set; } = 100;
        public double SleepSec { get; set; } = 0.25;
        public double WaitSec { get; set; } = 0.125;
    }
}
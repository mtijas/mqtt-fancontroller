#include "epaper.hpp"

Epaper::Epaper(Observable *events, int update_interval, Epd *epd, Paint *paint)
    : TimedComponent(events, update_interval)
{
    this->display_ok = false;
    this->paint = paint;
    this->epd = epd;
}

void Epaper::setup()
{
    epd->LDirInit();
    epd->Clear();

    display_ok = true;
}

void Epaper::notify(String event, String data)
{
}

void Epaper::update()
{
    events->notify_observers("d1", "on");
    if (!display_ok)
    {
        return;
    }

    clearDisplay();

    String time = String(millis() / 1000);
    String line = "Time: " + time;
    paintString(line, &Font24, 4, 4, 200, 32, UNCOLORED, COLORED);
    positionPaintToDisplay(paint, 0, 0);

    epd->DisplayFrame();
    events->notify_observers("d2", "on");
}

void Epaper::paintString(
    String data,
    sFONT *font,
    int x,
    int y,
    int width,
    int height,
    int color = COLORED,
    int background = UNCOLORED)
{
    paint->SetWidth(width);
    paint->SetHeight(height);
    paint->Clear(background);

    char char_buf[30];
    data.toCharArray(char_buf, 30);
    paint->DrawStringAt(x, y, char_buf, &Font24, color);
}

void Epaper::positionPaintToDisplay(Paint *paint, int x, int y)
{
    epd->SetFrameMemory(paint->GetImage(), x, y, paint->GetWidth(), paint->GetHeight());
}

void Epaper::clearDisplay()
{
    paint->SetWidth(200);
    paint->SetHeight(40);
    paint->Clear(UNCOLORED);
    for (int i = 0; i < 8; i++)
    {
        epd->SetFrameMemory(paint->GetImage(), 0, i * 40, paint->GetWidth(), paint->GetHeight());
    }
}

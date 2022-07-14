#include "epaper.hpp"

Epaper::Epaper(Observable *events, int update_interval)
    : TimedComponent(events, update_interval)
{
    this->display_ok = false;
    paint = &Paint(image, 0, 0);
    epd = &Epd();
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
    if (!display_ok) {
        return;
    }

    paint->SetWidth(200);
    paint->SetHeight(30);

    //paint->Clear(UNCOLORED);

    char char_buf[10];
    String(millis() / 1000).toCharArray(char_buf, 10);
    paint->DrawStringAt(30, 4, char_buf, &Font16, COLORED);
    events->notify_observers("d1", "on");

    epd->SetFrameMemory(paint->GetImage(), 0, 10, paint->GetWidth(), paint->GetHeight());

    epd->DisplayFrame();
    events->notify_observers("d2", "on");
}

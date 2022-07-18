#include "epaper.hpp"

Epaper::Epaper(Paint *paint, Epd *epd, int width, int height)
{
    this->display_ok = false;
    this->paint = paint;
    this->epd = epd;
    this->width = width;
    this->height = height;
}

void Epaper::setup()
{
    epd->LDirInit();
    epd->Clear();

    display_ok = true;
}

void Epaper::fullUpdate()
{
    if (!display_ok)
    {
        return;
    }

    epd->DisplayFrame();
}

void Epaper::partUpdate()
{
    if (!display_ok)
    {
        return;
    }

    epd->DisplayPartFrame();
}

void Epaper::printString(
    String data,
    int font_size,
    int x,
    int y,
    int width)
{
    printString(data, font_size, x, y, width, COLORED, UNCOLORED);
}

void Epaper::printString(
    String data,
    int font_size,
    int x,
    int y,
    int width,
    int color,
    int background)
{
    if (!display_ok)
    {
        return;
    }

    paint->SetWidth(width);
    paint->SetHeight(font_size + 4);
    paint->Clear(background);

    sFONT *font = getFont(font_size);

    char char_buf[30];
    data.toCharArray(char_buf, 30);
    paint->DrawStringAt(2, 2, char_buf, font, color);
    epd->SetFrameMemory(paint->GetImage(), x, y, paint->GetWidth(), paint->GetHeight());
}

void Epaper::clearDisplay()
{
    if (!display_ok)
    {
        return;
    }

    paint->SetWidth(200);
    paint->SetHeight(40);
    paint->Clear(UNCOLORED);
    for (int i = 0; i < 8; i++)
    {
        epd->SetFrameMemory(paint->GetImage(), 0, i * 40, paint->GetWidth(), paint->GetHeight());
    }
    epd->DisplayFrame();
}

sFONT *Epaper::getFont(int font_size)
{
    switch (font_size)
    {
    case 12:
        return &Font12;
        break;

    case 20:
        return &Font20;
        break;

    default:
        return &Font12;
        break;
    }
}

int Epaper::getWidth() {
    return width;
}

int Epaper::getHeight() {
    return height;
}

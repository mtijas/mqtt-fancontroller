#ifndef OBSERVABLE_H
#define OBSERVABLE_H

#include "iobservable.hpp"

class Observable : public IObservable {
  private:
    Observer *observers[50];
    int arr_length;

  public:
    Observable();
    void register_observer(Observer *observer);
    void notify_observers(const char *event, int payload);
};

#endif

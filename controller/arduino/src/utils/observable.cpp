#include "observable.hpp"

using namespace std;

/**
 * @brief Register a new Observer
 *
 * @param observer
 */
void Observable::register_observer(Observer *observer)
{
    if (arr_length < 50)
    {
        observers[arr_length] = observer;
        arr_length++;
    }
}

/**
 * @brief Notify all registered Observers of an event, with payload
 *
 * @param payload
 */
void Observable::notify_observers(const char *event, uint16_t payload)
{
    for (int i = 0; i < arr_length; i++)
    {
        observers[i]->notify(event, payload);
    }
}

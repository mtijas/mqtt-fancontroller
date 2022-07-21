#include "observable.hpp"

using namespace std;

/**
 * @brief Register a new Observer
 *
 * @param observer
 */
void Observable::register_observer(Observer* observer)
{
    if (arr_length < 50)
    {
        observers[arr_length] = observer;
        arr_length++;
    }
}

/**
 * @brief Notify all registered Observers of an event, with data
 *
 * @param data
 */
void Observable::notify_observers(const char *event, const uint8_t channel, const char *data)
{
    for (int i = 0; i < arr_length; i++)
    {
        observers[i]->notify(event, channel, data);
    }
}

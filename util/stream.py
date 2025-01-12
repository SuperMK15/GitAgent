def create_stream_result_function(result):
    """
    Takes a result object and returns a function `stream_result` 
    that yields content-delta messages.

    :param result: Iterable object with events to process.
    :return: A function object `stream_result`.
    """
    def stream_result():
        """
        Generator function that iterates over the result and yields 
        the content text for events of type 'content-delta'.
        """
        for event in result:
            if event:
                if event.type == "content-delta":
                    print(event.delta.message.content.text)
                    yield event.delta.message.content.text

    return stream_result

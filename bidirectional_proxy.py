'''Basic implementation of a bidirectional proxy, starts 2 tcp streams and waits for data
in the source, to pass onto the sink.'''
import anyio
import anyio.abc._sockets


async def one_way_proxy(source: anyio.abc._sockets.SocketStream, sink: anyio.abc._sockets.SocketStream):
    while True:
        data = await source.receive(1000)

        if not data:
            await source.send_eof()
            break

        await sink.send(data)


async def two_way_proxy(a: anyio.abc._sockets.SocketStream, b: anyio.abc._sockets.SocketStream) -> None:
    async with anyio.create_task_group() as tg:
        tg.start_soon(one_way_proxy, a, b)
        tg.start_soon(one_way_proxy, b, a)


async def main() -> None:
    a = await anyio.connect_tcp('localhost', 12345)
    b = await anyio.connect_tcp('localhost', 54321)

    async with a, b:
        await two_way_proxy(a, b)


if __name__ == '__main__':
    anyio.run(main)
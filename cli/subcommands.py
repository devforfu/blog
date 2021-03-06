from argparse import ArgumentParser, ArgumentError, ArgumentTypeError
from functools import partial
import json
from os.path import exists
import matplotlib.pyplot as plt


def main():
    parser = create_parser()
    args = parser.parse_args()
    params = {
        'stdin': vars(args),
        'json': getattr(args, 'config', None)
    }[args.command]
    f, ax = plt.subplots(1, 1, figsize=params['canvas_size'])
    if params['hide_axes']:
        ax.set_axis_off()
    if params['show_grid']:
        ax.grid(True)
    ax.plot(*params['points'])
    fmt = params['image_format']
    f.tight_layout()
    f.savefig(f'{params["out"]}.{fmt}', format=fmt)


def create_parser():
    parser = ArgumentParser()

    # -----------------
    # common parameters
    # -----------------

    parser.add_argument(
        '-f', '--format',
        dest='image_format', metavar='FMT', default='png',
        choices=['png', 'svg', 'pdf'],
        help='Output image format (choices: %(choices)s, default: %(default)s)'
    )
    parser.add_argument(
        '-o', '--out',
        default='output',
        help='Path to the output image file (default: %(default)s)'
    )

    commands = parser.add_subparsers(dest='sub-command')
    commands.required = True

    # -------------------------------
    # stdio-based plotting parameters
    # -------------------------------

    stdin_cmd = commands.add_parser('stdin')
    stdin_cmd.set_defaults(command='stdin')
    stdin_cmd.add_argument(
        '-sz', '--size',
        type=canvas_dimensions,
        dest='canvas_size', metavar='SZ', default='8x6',
        help='Canvas size (default: %(default)s)'
    )
    stdin_cmd.add_argument(
        '-p', '--points',
        type=list_of_points,
        metavar='PTS', required=True,
        help='List of points to plot'
    )
    stdin_cmd.add_argument(
        '--hide-axes',
        default=False, action='store_true',
        help='Suppress axes drawing functionality'
    )
    stdin_cmd.add_argument(
        '--show-grid',
        default=False, action='store_true',
        help='Show grid on plot'
    )

    # ------------------------------
    # json-based plotting parameters
    # ------------------------------

    json_cmd = commands.add_parser('json')
    json_cmd.set_defaults(command='json')
    json_cmd.add_argument(
        '-j', '--json',
        required=True,
        dest='config', type=partial(load_json_file, default={
            'canvas_size': [8, 6],
            'show_grid': True,
            'hide_axes': False
        }),
        help='Path to json file'
    )

    return parser


def list_of_points(value: str) -> tuple:
    """Ensures that `points` argument contains a valid sequence of values."""

    try:
        points = value.split(';')
        xs, ys = [], []
        for point in points:
            x, y = point.split(',')
            xs.append(float(x))
            ys.append(float(y))
        return xs, ys
    except ValueError:
        raise ArgumentTypeError('should have format: 1,2;2,3;3,4')


def canvas_dimensions(value: str) -> tuple:
    """Ensures that `canvas_size` represents a valid (w, h) tuple."""

    try:
        w, h = [int(v) for v in value.split('x')]
        return w, h
    except (ValueError, TypeError):
        raise ArgumentTypeError('should have format: 3x4')


def load_json_file(value: str, default: dict=None) -> str:
    """Ensures that file exists and contains valid JSON object.

    If the `default` parameter is provided, fills the keys missing in the
    loaded JSON object with the keys from the `default` dictionary.
    """
    if not exists(value):
        raise ArgumentError(value, 'file doesn\'t exist')
    try:
        with open(value) as file:
            content = json.load(file)
        if default is not None:
            for key, value in default.items():
                if key not in content:
                    content[key] = value
        return content
    except json.JSONDecodeError:
        raise ArgumentTypeError('invalid JSON file')


if __name__ == '__main__':
    main()

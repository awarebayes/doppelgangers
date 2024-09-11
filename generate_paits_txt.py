import shutil
import numpy as np
from scipy.special import softmax
import os
import argparse
from doppelgangers.utils.database import COLMAPDatabase
import sqlite3

parser = argparse.ArgumentParser(description="Generate pairs.txt")
parser.add_argument("--output_path", type=str, help="path to output results")
parser.add_argument(
    "--threshold",
    default=0.8,
    type=float,
    help="doppelgangers threshold: smaller means more pairs will be included, larger means more pairs will be filtered out",
)


def pair_id_to_image_ids(pair_id):
    image_id2 = pair_id % 2147483647
    image_id1 = int((pair_id - image_id2) / 2147483647)
    return image_id1, image_id2


def get_image_dict(database_path) -> dict[int, str]:
    image_dict: dict[int, str] = {}
    db = None
    try:
        db = COLMAPDatabase.connect(database_path)
        cursor = db.cursor()
        sqlite_pairs_query = f"SELECT * from images"
        cursor.execute(sqlite_pairs_query)
        print(sqlite_pairs_query)
        rows = cursor.fetchall()
        for row in rows:
            cam_id = row[0]
            image_name = row[1]
            image_dict[cam_id] = image_name
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to delete multiple records from sqlite table", error)
    finally:
        if db:
            db.close()
    return image_dict


def get_pairs(database_path) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    db = None
    try:
        db = COLMAPDatabase.connect(database_path)
        cursor = db.cursor()
        sqlite_pairs_query = f"SELECT * from two_view_geometries"
        cursor.execute(sqlite_pairs_query)
        print(sqlite_pairs_query)
        rows = cursor.fetchall()
        for row in rows:
            pair_id = row[0]
            first, second = pair_id_to_image_ids(pair_id)
            pairs.append((first, second))
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to delete multiple records from sqlite table", error)
    finally:
        if db:
            db.close()
    return pairs


if __name__ == "__main__":
    args = parser.parse_args()
    pair_probability_file = os.path.join(args.output_path, "pair_probability_list.npy")
    pair_path = os.path.join(args.output_path, "pairs_list.npy")
    database_path = os.path.join(
        args.output_path, f"database_threshold_{args.threshold:.3f}.db"
    )
    pairs_txt = os.path.join(args.output_path, f"pairs_{args.threshold:.3f}.txt")

    pairs = get_pairs(database_path)
    images = get_image_dict(database_path)
    image_pairs: list[tuple[str, str]] = []
    for p in pairs:
        first = images[p[0]]
        second = images[p[1]]
        image_pairs.append((first, second))

    with open(pairs_txt, "w") as f:
        for i in image_pairs:
            f.write(f"{i[0]} {i[1]}\n")

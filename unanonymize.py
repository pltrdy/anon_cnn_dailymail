#!/usr/bin/env python
import os
import utils


def main(args):
    def remove_eol(line):
        return line.replace("\n", "")

    # print(args)

    f = open(args.file)
    fl = open(args.entities_file_list)
    out = open(args.output, 'w')
    count = 0
    while True:
        text = f.readline()
        entity_filename = fl.readline()
        if not text and not entity_filename:
            print("Both files ends")
            break
        if not text:
            print("[WARNING] Text ends")
            break
        if not entity_filename:
            print("[WARNING] Entity ends")
            break

        if len(text) == 0:
            raise ValueError("Empty line %d in text file" % count)
        if len(entity_filename) == 0:
            raise ValueError("Empty line %d in entity file" % count)

        text = remove_eol(text)
        entity_filename = remove_eol(entity_filename)
        entity_path = os.path.join(args.entities_dir, "%s.entities"
                                   % entity_filename)
        entity_mapping = {}

        with open(entity_path) as entities:
            for entity_line in entities:
                parts = remove_eol(entity_line).split(":")
                tag = parts[0]
                value = " ".join(parts[1:])
                entity_mapping[tag] = value

        new_text = utils.replace_entity(entity_mapping, text, reverse=False)
        print(new_text, file=out)
        count += 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Replace entity tags by words')
    parser.add_argument("-f", "--file", help="Text file", required=True)
    parser.add_argument("-fl", "--entities_file_list",
                        help="Entity files list", required=True)
    parser.add_argument("-d", "--entities_dir", required=True,
                        help="Entity files dir")
    parser.add_argument("-o", "--output", help="Output file", required=True)
    args = parser.parse_args()

    main(args)

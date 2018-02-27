#!/usr/bin/env python
import os
import re
from utils import hashhex, warning, fix_missing_period, line_to_sentence, replace_entity


def tokenize_dir(src_dir, dst_dir, tokenizer_mapping_path="./tok_mapping.txt"):
    """Tokenzie each files of root/dirname to root/"tok_"+dirname
    """
    print("Tokenizing directory:\n\t* src: %s\n\t* dst: %s\n\t* map file: %s"
          % (src_dir, dst_dir, tokenizer_mapping_path))
    with open(tokenizer_mapping_path, "w") as f:
        for filename in os.listdir(src_dir):
            src_path = os.path.join(src_dir, filename)
            if not os.path.isfile(src_path):
                continue
            dst_path = os.path.join(dst_dir, filename)
            f.write("%s \t %s\n" % (src_path, dst_path))

    import subprocess
    command = ['java', 'edu.stanford.nlp.process.PTBTokenizer',
               '-ioFileList', '-preserveLines', tokenizer_mapping_path]

    print("Running command:\n", " ".join(command))
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        exit()
        pass  # handle errors in the called executable
    except OSError:
        exit()
        pass  # executable not found
    print("Tokenizer done")


def process_lines(lines, entity_mapping):
    o = " ".join([line_to_sentence(b) for b in lines])
    o = o.lower()
    o = replace_entity(entity_mapping, o)
    return o


def process_set(question_filenames, stories_root, output_root):
    """Process a set of question filenames.
       For each question file:
        * reads the associated story files
        * retag entities (per document notation); 
        * fixes some stuff (whitespace, case)
        * outputs story, highlight and entities in three files:
            output_root/<hash>.{story, highlight, entities}
    """
    n_stories = sum([1 if os.path.isfile(os.path.join(stories_root, _)) else 0
                     for _ in os.listdir(stories_root)])

    stories_out = open(os.path.join(output_root, "stories"), "w")
    highlights_out = open(os.path.join(output_root, "highlights"), "w")
    filelist_out = open(os.path.join(output_root, "files"), "w")

    print(stories_root)
    print("%d stories" % (n_stories))
    processed_hashes = []
    for filename in question_filenames:
        with open(filename) as f:
            if len(processed_hashes) == n_stories:
                break

            try:
                line = f.readline().replace("\n", "")
            except:
                warning("[WARNING] Empty file %s" % filename)
                continue

            # looking for corresponding story
            b_url = line.encode("utf-8")
            h = hashhex(b_url)
            if h in processed_hashes:
                # warning("[WARNING] Already processed hash %s" % h)
                continue
            processed_hashes += [h]

            story_name = "%s.story" % h
            story_path = os.path.join(stories_root, story_name)
            if not os.path.isfile(story_path):
                warning("[WARNING] No story file:\n\t\t%s\nfor question:\t%s" % (
                    story_path, filename))
                continue

            lines = f.readlines()

            # here, qstory contains tokenzied, anonymous, stories
            qstory = lines[1]
            qquestion = lines[3]
            qanswer = lines[5]
            qentities = lines[7:]

            nentities = len(qentities)

            # {new_tag: value}
            entity_new_mapping = {}

            # {old_tag: new_tag}
            entity_remapping = {}
            # we remap entity numbers locally (per document)
            for (i, entity) in enumerate(qentities):
                parts = entity.split(":")
                tag = parts[0]
                value = " ".join(parts[1:])

                value = " ".join(value.split()).lower()
                new_tag = "@entity%d" % i
                entity_remapping[tag] = new_tag
                entity_new_mapping[new_tag] = value

            bullets, highlights = [], []
            next_highlight = False
            with open(story_path) as story_file:
                for line in story_file:
                    if line is None:
                        break
                    if line == "\n":
                        continue
                    if "@highlight" in line:
                        next_highlight = True
                        continue
                    if next_highlight:
                        highlights += [line]
                    else:
                        bullets += [line]
                    next_highlight = False

            #ref_story_path = os.path.join(output_root, "%s.ref" % h)
            # with open(ref_story_path, 'w') as out_ref:
            #    story = replace_entity(entity_remapping, qstory)
            #    out_ref.write(story)

            story = process_lines(bullets, entity_new_mapping)
            stories_out.write(story+"\n")

            highlight = process_lines(highlights, entity_new_mapping)
            highlights_out.write(highlight+"\n")

            filelist_out.write(h)

            entities_path = os.path.join(output_root, "%s.entities" % h)
            with open(entities_path, 'w') as out_entities:
                entities = "\n".join(["%s:%s" % (k, v)
                                      for (k, v) in entity_new_mapping.items()])
                out_entities.write(entities)


def _process(questions_root, stories_root, output_root):
    processed_story = []
    questions_files = {}
    for dataset in ["training", "validation", "test"]:
        dataset_root = os.path.join(questions_root, dataset)
        filenames = [os.path.join(questions_root, dataset, _filename)
                     for _filename in os.listdir(dataset_root)]
        print("Processing %s (%d question files)" % (dataset, len(filenames)))
        set_output_root = os.path.join(output_root, dataset)

        os.makedirs(set_output_root, exist_ok=True)
        process_set(filenames, stories_root, set_output_root)
        # run for f in *.story; do echo "$f" >> train.story; done


def main(skip_tokenizer=False):
    dataset_root = "/home/pltrdy/cnndm4"
    output_root = "/home/pltrdy/cnndm4/processed"
    os.makedirs(output_root, exist_ok=True)

    for dataset in ["cnn", "dailymail"]:
        print("Working on %s:" % dataset)
        root = os.path.join(dataset_root, dataset)
        questions, stories_root = [
            os.path.join(root, _) for _ in ["questions", "stories"]]

        tok_stories_root = os.path.join(output_root, "tok_stories")

        if not skip_tokenizer:
            os.makedirs(tok_stories_root, exist_ok=True)
            tokmap = os.path.join(output_root, "tokmap_%s_story.txt" % dataset)
            tokenize_dir(stories_root, tok_stories_root, tokmap)

        _process(questions, tok_stories_root, output_root)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Process CNN/DailyMail dataset')
    parser.add_argument("--skip_tokenizer", action="store_true")
    args = parser.parse_args()

    main(skip_tokenizer=args.skip_tokenizer)

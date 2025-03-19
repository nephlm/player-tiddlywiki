import argparse
import re

from tiddlywiki_parser import readers, tiddlywiki

DEFAULT_PRIVATE = True
PRIVATE_TAGS = ["gm", "private"]
PUBLIC_TAGS = ["player", "public"]


def fix_tags(tags):
    matches = re.findall(r"\[\[(.*?)\]\]", tags)  # Extract contents inside [[ ]]
    cleaned_text = re.sub(r"\[\[.*?\]\]", "", tags).strip()
    return matches + cleaned_text.split()


def extract_from_private(tiddler):
    pattern = rf"@@\.({'|'.join(map(re.escape, PUBLIC_TAGS))})[\s\S]*?@@"
    matches = [match.group(0) for match in re.finditer(pattern, tiddler.raw_text)]
    if matches:
        tiddler.raw_text = f"<pre>\n {'\n\n'.join(matches)} \n</pre>"
        print(tiddler.raw_text)
    else:
        return tiddler.attrs["title"]


def clean_public(tiddler):
    pattern = rf"@@\.({'|'.join(map(re.escape, PRIVATE_TAGS))})[\s\S]*?@@"
    print(tiddler.text)
    print(tiddler.raw_text)
    tiddler.raw_text = re.sub(pattern, "", tiddler.raw_text).strip()
    print(tiddler.raw_text)


def clean_wiki(wiki):
    delete_list = []
    for tiddler in wiki.tiddlers:
        private = False or DEFAULT_PRIVATE
        tags = fix_tags(tiddler.attrs["tags"])
        for tag in tags:
            if tag in PUBLIC_TAGS:
                private = False
            if tag in PRIVATE_TAGS:
                private = True
                break
        if private:
            to_delete_title = extract_from_private(tiddler)
            if to_delete_title:
                delete_list.append(to_delete_title)
        else:
            clean_public(tiddler)
    return wiki, delete_list


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="The tiddlywiki src.  May be a path or url.")
    parser.add_argument("dst", help="The tiddlywiki dest.  Must be a file path.")
    args = parser.parse_args()

    content = readers.read(args.src)
    wiki = tiddlywiki.TiddlyWiki(content)
    wiki, delete_list = clean_wiki(wiki)
    new_wiki = wiki.remake(delete_list)
    with open(args.dst, "w", encoding="utf8") as f:
        f.write(new_wiki)
    print("Player wiki written")


if __name__ == "__main__":
    main()

import json
import sys
import os

print("Starting script...")

# Add Assets/module to path
sys.path.append(os.path.join(os.path.dirname(__file__), "Assets", "module"))

from Assets.module.map_generator import MapGenerator


def main():
    maps = []

    print("Generating 6x6 Map...")
    gen6 = MapGenerator(6)
    map6 = gen6.create_map()
    if map6:
        maps.append(map6)
        print("Success!")
    else:
        print("Failed 6x6")

    print("Generating 8x8 Map...")
    gen8 = MapGenerator(8)
    map8 = gen8.create_map()
    if map8:
        maps.append(map8)
        print("Success!")
    else:
        print("Failed 8x8")

    print("Generating 10x10 Map...")
    gen10 = MapGenerator(10)
    map10 = gen10.create_map()
    if map10:
        maps.append(map10)
        print("Success!")
    else:
        print("Failed 10x10")

    print("Generating 12x12 Map...")
    gen12 = MapGenerator(12)
    map12 = gen12.create_map()
    if map12:
        maps.append(map12)
        print("Success!")
    else:
        print("Failed 12x12")

    print("Generating 16x16 Map...")
    gen16 = MapGenerator(16)
    map16 = gen16.create_map()
    if map16:
        maps.append(map16)
        print("Success!")
    else:
        print("Failed 16x16")

    # Custom JSON formatting to align map_data
    json_str = json.dumps(maps, indent=4)

    lines = json_str.split("\n")
    formatted_lines = []
    iterator = iter(lines)

    for line in iterator:
        if '"map_data": [' in line:
            formatted_lines.append(line)

            for subline in iterator:
                stripped = subline.strip()

                if stripped == "]" or stripped == "],":
                    formatted_lines.append(subline)
                    break

                if stripped == "[":
                    row_elements = []
                    for element_line in iterator:
                        el_stripped = element_line.strip()
                        if el_stripped.startswith("]"):
                            # End of row
                            # Format elements to be aligned
                            formatted_elements = []
                            for el in row_elements:
                                # Pad to 4 chars (e.g. "" -> ""  , "tl" -> "tl")
                                formatted_elements.append(f"{el:<4}")

                            row_str = (
                                "            [" + ", ".join(formatted_elements) + "]"
                            )
                            if el_stripped == "],":
                                row_str += ","
                            formatted_lines.append(row_str)
                            break
                        else:
                            row_elements.append(el_stripped.rstrip(","))

        elif '"player_start": [' in line or '"stair_position": [' in line:
            if "]" in line:
                formatted_lines.append(line)
                continue

            # Format simple coordinate lists [x, y]
            key = line.split(":")[0]
            coords = []
            for subline in iterator:
                stripped = subline.strip()
                if stripped.startswith("]"):
                    formatted_lines.append(
                        f"{key}: [{', '.join(coords)}]{stripped[1:]}"
                    )
                    break
                coords.append(stripped.rstrip(","))

        elif (
            '"zombie_starts": [' in line
            or '"scorpion_starts": [' in line
            or '"trap_pos": [' in line
            or '"key_pos": [' in line
            or '"gate_pos": [' in line
        ):

            if "]" in line:
                formatted_lines.append(line)
                continue

            # Format list of lists [[x, y, type], ...]
            formatted_lines.append(line)
            for subline in iterator:
                stripped = subline.strip()
                if stripped == "]" or stripped == "],":
                    formatted_lines.append(subline)
                    break

                if stripped == "[":
                    entity_coords = []
                    for element_line in iterator:
                        el_stripped = element_line.strip()
                        if el_stripped.startswith("]"):
                            row_str = "            [" + ", ".join(entity_coords) + "]"
                            if el_stripped == "],":
                                row_str += ","
                            formatted_lines.append(row_str)
                            break
                        entity_coords.append(el_stripped.rstrip(","))

        else:
            formatted_lines.append(line)

    with open("generated_maps.json", "w") as f:
        f.write("\n".join(formatted_lines))

    print("Maps saved to generated_maps.json")


if __name__ == "__main__":
    main()

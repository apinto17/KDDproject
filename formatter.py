




def main():
    file = open("categories.txt", "r+")
    res = ""
    for line in file:
        line = line[1:len(line) - 2].strip()
        line = "\"" + line + "\",\n"
        res += line

    print(res)




if(__name__ == "__main__"):
    main()

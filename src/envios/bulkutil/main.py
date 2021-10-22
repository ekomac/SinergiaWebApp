from extractor import Extractor


def main():
    end = False
    while not end:
        try:
            extracto = Extractor()
            path = input("Indicá el path del archivo: ")
            csv = extracto.get_shipments_as_csv_str(path)
            with open('result.csv', 'w') as doc:
                doc.write(csv)
            print("Listo!")
        except KeyboardInterrupt:
            end = True


if __name__ == '__main__':
    main()

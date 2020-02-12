# ud_vs_sud
Comparing the learnability of two approaches to headedness for dependency grammars

## PLAN

1. Pobrać dotychczasowe korpusy w wersji UD i SUD, 2.4 i policzyć statystyki nieprojektywności
2. Na podstawie m.in. pkt 1., oraz konsultacji z prof. Przepiórkowskim (np. na temat wpływu automatycznego tagowania) i literaturą, wypracować metodę ewaluacji jakości korpusów, i dokonać selekcji korpusów.
3. Przygotować listę parserów [Combo, spacy, HSE] (również pod wpływem uwag recenzentów), i podjąć zewnętrznych embeddingów 
4. Zastanowić się nad ewentualną modyfikacją kodu konwertera UD->SUD
5. Poszukać alternatywnych sposobów ewaluacji parserów (wziąć pod uwagę korpus PUD, różne zadania nlp)
6. 

## Zadania:
- dodać globalną opcję pomijania interpunkcji, która modyfikowałaby działanie wszystkich skryptów na to wrażliwych
- pobrać embeddingi dla interesujących języków, facebook udostępnia wektory dla 157 języków: https://fasttext.cc/docs/en/crawl-vectors.html


Entropia etykiet bez wyjątku niższa w SUD

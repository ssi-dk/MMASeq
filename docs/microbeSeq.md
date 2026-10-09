# MMAseq in the Danish NMational Surveillance
MMAseq has been developped as part of [MicrobeSeq](https://microbeseq.ssi.dk/).

Bacterial samples collected in the Danish National surveillance of antimicrobial resistance are transported to Statens Serum Institute (SSI).
From here bacterial isolates are collected and grown from the samples. Whole genome sequencing is performed on DNA extracts from these bacterial isolates, and raw sequencing data processing and general typing are performed through the quality assessment module of [MicrobeSeq](https://microbeseq.ssi.dk/), while species specific analysis is performed using MMAseq.
This document describes the species specific analysis performed at SSI for the Danish National Surveillance

## Species Specific analysis in The Danish National Reference Laboratory for Antimicrobial Resistance
Overall, bacterial isolates are distributed into major groups and analyzed accordingly. The major groups are:
* Actinobacillus pleuropneumoniae from Pig lings (APP)
* Carbapenemase Producing Organisms (CPO)
* Extended Spectrum Beta-Lactamase E. coli (ESBL)
* Methicillin-resistant Staphylococcus aureus (MRSA)
* Vancomycin Resistant Enterococci (VRE)

### APP
Surface capsule composition is analysed and a serovar is determined using [Serovar_detector](https://github.com/KasperThystrup/serovar_detector) with raw reads.

#### Config file
```
serovar_detector:
    reads: True
```

### CPO
Plasmid replicon detection is performed using plasmidfinder, accepting a template coverage and identitity of at least 80% for small plasmids and a template coverage and identity of at least 90 % for other plasmids.
Specific plasmid outbreak markers are detected using blastn against sequences specific to certain outbreak markers, target sequences currently includes a specific [OXANDM](https://www.thelancet.com/journals/lanmic/article/PIIS2666-5247(26)00009-1/fulltext) marker.
E. coli isolates are further characterized by detecting FumC and FimH genes using kmeraligner (KMA) to map raw reads against sequences from pubMLST.
K. pneumoniae and K. oxytoca are further characterized using Kleborate with present modules `kpsc` and `kpso` respectively.

#### Config file(s)
```
plasmidfinder:
  options: "-l 80 -t 80"
  assembler: shovill

blastn:
  options: "-perc_identity 99.0"
  assembler: shovill
  database : OXAndm

# E. coli in addition
chtyper:
    database: fumCH 
    reads: True

# Klepsiella spp in addition

kleborate:
    options: --preset kpsc # or kpso for oxytoca
    assembler: shovill
```
#### ESBL
Plasmid replicon detection is performed using plasmidfinder, accepting a template coverage and identitity of at least 80% for small plasmids and a template coverage and identity of at least 90 % for other plasmids.
Specific plasmid outbreak markers are detected using blastn against sequences specific to certain outbreak markers, target sequences currently includes a specific [OXANDM](https://www.thelancet.com/journals/lanmic/article/PIIS2666-5247(26)00009-1/fulltext) marker.
E. coli isolates are further characterized by detecting FumC and FimH genes using KMA to map raw reads against sequences from pubMLST.

#### Config file
```
plasmidfinder:
  options: "-l 80 -t 80"
  assembler: shovill

blastn:
  options: "-perc_identity 99.0"
  assembler: shovill
  database : OXAndm

chtyper:
    database: fumCH 
    reads: True
```

### VRE
Plasmid replicon detection is performed using plasmidfinder, accepting a template coverage and identitity of at least 80% for small plasmids and a template coverage and identity of at least 90 % for other plasmids.
Specific plasmid outbreak markers are detected using blastn against sequences specific to certain outbreak markers, target sequences currently includes a specific [OXANDM](https://www.thelancet.com/journals/lanmic/article/PIIS2666-5247(26)00009-1/fulltext) marker.
Linezolid resistance are determimed from analysing mutations of the 23S region as well as detection of optrA, cfr and poxtA are performed by mapping raw reads against reference sequences using KMA, for the 23 sequence, specific locations are analysed and SNP events are quantified.

#### Config file
```
plasmidfinder:
  options: "-l 80 -t 80"
  assembler: shovill

blastn:
  options: "-perc_identity 99.0"
  assembler: shovill
  database : OXAndm

lrefinder:
    database : [elmDB]
    reads: True

kmeraligner:
    database : [vancomycin, vancomycinOperon]
    reads: True
```
Vancomycin resistance conferring genes VanA, Vanb, and VanD alongside other supporter genes are detected by mapping raw reads against their sequences using KMA


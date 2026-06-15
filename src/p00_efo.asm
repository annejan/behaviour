// p00_efo.asm — EFO2 header (built -binfile, cat before p00.prg).
.import source "p00.sym"
.pc = $0000 "EfoHeader"
        .text "EFO2"
        .word $0000            // prepare
        .word setup
        .word interrupt
        .word $0000            // main
        .word $0000            // fadeout
        .word $0000            // cleanup
        .word $0000            // callmusic
        .byte 'S'              // i/o safe
        .byte 'P', $08, $08    // code page(s)
        .byte 'P', $40, $47    // screen + colour stage
        .byte 'P', $60, $7f    // bitmap
        .byte 'M', $03, $10    // install PLAY=$1003
        .byte $00

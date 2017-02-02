import sys
entry_name = "main"
file_name = "test.c"

header = "\t.file\t"+file_name+"\n\t,__text\n\t.globl "+entry_name+"\n\t.align 4"

func_start = "\n\t"+entry_name+":"+"\n\t"+".cfi_startproc\n\tpushq\t%rbp\nLtmp0:\n\t.cfi_def_cfa_offset 16\nLtmp1:\n\t.cfi_offset %rbp, -16\n\tmovq\t%rsp, %rbp\nLtmp2:\n\t.cfi_def_cfa_register %rbp"

func_end = "\n\t.cfi_endproc\n\n.subsections_via_symbols"

def add_header(fd):
    fd.write(header)

def gen_write_handler(fout):
    def write_to_file(ret_num):
        fout.write(func_start)
        fout.write("\n\tmovl\t$%d," %(ret_num) + "%eax")
        fout.write("\n\tpopq\t%rbp\n\tretq")
        fout.write(func_end)
    return write_to_file

if __name__ == "__main__":
    fin = open("source.c", 'r')
    fout = open("out.s", 'w')
    if fout is False:
        print "Cannot create OUTPUT file"
        exit
    add_header(fout)
    code_writer = gen_write_handler(fout)
    
    ret_num = 24
    code_writer(ret_num)
    fin.close()
    fout.close()

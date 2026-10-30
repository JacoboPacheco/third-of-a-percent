00000000000011d0 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi>:
    11d0:	test   %esi,%esi
    11d2:	jle    1203 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x33>
    11d4:	mov    (%rdi),%rax
    11d7:	mov    0x8(%rdi),%rcx
    11db:	sub    %rax,%rcx
    11de:	sar    $0x2,%rcx
    11e2:	mov    %esi,%edx
    11e4:	xor    %esi,%esi
    11e6:	xor    %edi,%edi
    11e8:	nopl   0x0(%rax,%rax,1)
    11f0:	cmp    %rdi,%rcx
    11f3:	je     1204 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x34>
    11f5:	mov    %esi,(%rax,%rdi,4)
    11f8:	inc    %rdi
    11fb:	add    $0x3,%esi
    11fe:	cmp    %rdi,%rdx
    1201:	jne    11f0 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x20>
    1203:	ret
    1204:	ud2
    1206:	cs nopw 0x0(%rax,%rax,1)

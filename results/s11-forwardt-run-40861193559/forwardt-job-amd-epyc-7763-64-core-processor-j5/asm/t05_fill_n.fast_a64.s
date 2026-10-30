0000000000001200 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi>:
    1200:	test   %esi,%esi
    1202:	jle    1253 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x53>
    1204:	mov    (%rdi),%rax
    1207:	mov    0x8(%rdi),%rcx
    120b:	sub    %rax,%rcx
    120e:	sar    $0x2,%rcx
    1212:	mov    %esi,%edx
    1214:	xor    %esi,%esi
    1216:	xor    %edi,%edi
    1218:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1227:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1236:	cs nopw 0x0(%rax,%rax,1)
    1240:	cmp    %rdi,%rcx
    1243:	je     1254 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x54>
    1245:	mov    %esi,(%rax,%rdi,4)
    1248:	inc    %rdi
    124b:	add    $0x3,%esi
    124e:	cmp    %rdi,%rdx
    1251:	jne    1240 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x40>
    1253:	ret
    1254:	ud2
    1256:	cs nopw 0x0(%rax,%rax,1)

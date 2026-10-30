00000000000011d0 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi>:
    11d0:	test   %esi,%esi
    11d2:	jle    124e <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x7e>
    11d4:	mov    (%rdi),%rcx
    11d7:	mov    %esi,%edx
    11d9:	mov    %edx,%eax
    11db:	and    $0x3,%eax
    11de:	cmp    $0x4,%esi
    11e1:	jae    11e7 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x17>
    11e3:	xor    %esi,%esi
    11e5:	jmp    122a <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x5a>
    11e7:	and    $0x7ffffffc,%edx
    11ed:	mov    $0x9,%edi
    11f2:	xor    %esi,%esi
    11f4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1200:	lea    -0x9(%rdi),%r8d
    1204:	mov    %r8d,(%rcx,%rsi,4)
    1208:	lea    -0x6(%rdi),%r8d
    120c:	mov    %r8d,0x4(%rcx,%rsi,4)
    1211:	lea    -0x3(%rdi),%r8d
    1215:	mov    %r8d,0x8(%rcx,%rsi,4)
    121a:	mov    %edi,0xc(%rcx,%rsi,4)
    121e:	add    $0x4,%rsi
    1222:	add    $0xc,%edi
    1225:	cmp    %rsi,%rdx
    1228:	jne    1200 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x30>
    122a:	test   %rax,%rax
    122d:	je     124e <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x7e>
    122f:	lea    (%rsi,%rsi,2),%edx
    1232:	lea    (%rcx,%rsi,4),%rcx
    1236:	xor    %esi,%esi
    1238:	nopl   0x0(%rax,%rax,1)
    1240:	mov    %edx,(%rcx,%rsi,4)
    1243:	inc    %rsi
    1246:	add    $0x3,%edx
    1249:	cmp    %rsi,%rax
    124c:	jne    1240 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x70>
    124e:	ret
    124f:	nop

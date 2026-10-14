0000000000001220 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
    1220:	mov    (%rdi),%rcx
    1223:	mov    0x8(%rdi),%rdx
    1227:	sub    %rcx,%rdx
    122a:	je     123c <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x1c>
    122c:	sar    $0x2,%rdx
    1230:	cmp    $0x4,%rdx
    1234:	jae    1240 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x20>
    1236:	xor    %esi,%esi
    1238:	xor    %eax,%eax
    123a:	jmp    12ae <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x8e>
    123c:	xor    %eax,%eax
    123e:	jmp    12a8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x88>
    1240:	mov    %rdx,%rsi
    1243:	and    $0xfffffffffffffffc,%rsi
    1247:	pxor   %xmm0,%xmm0
    124b:	xor    %eax,%eax
    124d:	pxor   %xmm1,%xmm1
    1251:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1260:	movq   (%rcx,%rax,4),%xmm2
    1265:	movq   0x8(%rcx,%rax,4),%xmm3
    126b:	pxor   %xmm4,%xmm4
    126f:	pcmpgtd %xmm2,%xmm4
    1273:	punpckldq %xmm4,%xmm2
    1277:	paddq  %xmm2,%xmm0
    127b:	pxor   %xmm2,%xmm2
    127f:	pcmpgtd %xmm3,%xmm2
    1283:	punpckldq %xmm2,%xmm3
    1287:	paddq  %xmm3,%xmm1
    128b:	add    $0x4,%rax
    128f:	cmp    %rax,%rsi
    1292:	jne    1260 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x40>
    1294:	paddq  %xmm0,%xmm1
    1298:	pshufd $0xee,%xmm1,%xmm0
    129d:	paddq  %xmm1,%xmm0
    12a1:	movq   %xmm0,%rax
    12a6:	jmp    12a9 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x89>
    12a8:	ret
    12a9:	cmp    %rsi,%rdx
    12ac:	je     12a8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x88>
    12ae:	movslq (%rcx,%rsi,4),%rdi
    12b2:	add    %rdi,%rax
    12b5:	inc    %rsi
    12b8:	jmp    12a9 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x89>
    12ba:	nopw   0x0(%rax,%rax,1)

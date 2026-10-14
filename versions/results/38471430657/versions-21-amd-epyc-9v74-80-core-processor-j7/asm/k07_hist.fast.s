0000000000001220 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     1256 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x36>
    122c:	sar    $0x2,%rcx
    1230:	mov    (%rdi),%rdx
    1233:	mov    0x8(%rdi),%rsi
    1237:	sub    %rdx,%rsi
    123a:	sar    $0x2,%rsi
    123e:	xor    %edi,%edi
    1240:	movzbl (%rax,%rdi,4),%r8d
    1245:	cmp    %r8,%rsi
    1248:	jbe    1257 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x37>
    124a:	incl   (%rdx,%r8,4)
    124e:	inc    %rdi
    1251:	cmp    %rdi,%rcx
    1254:	jne    1240 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x20>
    1256:	ret
    1257:	ud2
    1259:	nopl   0x0(%rax)
